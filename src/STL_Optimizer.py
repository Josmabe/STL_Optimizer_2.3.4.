"""
=========================================================
STL OPTIMIZER

Main program with isolated STL worker processes.

Each STL is processed in its own operating-system process.
If one file exceeds the configured timeout, that worker is
terminated and the application continues with the next STL.

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

import copy
import multiprocessing as mp
import queue
import traceback
from pathlib import Path
from time import perf_counter

from config_API import (
    ENABLE_CONVEX_HULL_FALLBACK,
    ENABLE_PROCESS_TIMEOUT,
    OVERWRITE_EXISTING,
    PROCESS_TIMEOUT_SECONDS,
    SAVE_CONVEX_HULL_IMAGE,
    SAVE_CONVEX_HULL_STL,
    SEARCH_SUBDIRECTORIES,
    TERMINATE_GRACE_SECONDS,
)
from file_manager import FileManager
from geometry_utils import GeometryUtils
from logger import Logger
from mass_processor import MassProcessor
from mesh_processor import MeshProcessor
from repair_processor import RepairProcessor
from time_utils import format_elapsed_time
from watertight_processor import WatertightProcessor


def _elapsed_since(start_time):
    return perf_counter() - start_time


def process_stl_worker(input_file_text, result_queue):
    """Processes one STL inside an isolated child process."""
    input_file = Path(input_file_text)
    logger = Logger()
    worker_start_time = perf_counter()
    stage_timings = {}

    try:
        file_manager = FileManager()
        processor = MeshProcessor()
        repair = RepairProcessor()

        report_path = file_manager.log_path(input_file)
        output_path = file_manager.output_path(input_file)

        logger.start_log(report_path)
        logger.begin_file(input_file.name)

        if output_path.exists() and not OVERWRITE_EXISTING:
            logger.message(
                f"Skipped: '{input_file.name}' "
                "(optimized file already exists)."
            )
            elapsed_seconds = _elapsed_since(worker_start_time)
            logger.set_elapsed_time(elapsed_seconds)
            logger.summary()
            result_queue.put({
                "status": "skipped",
                "input_file": str(input_file),
                "output_file": str(output_path),
                "report_file": str(report_path),
                "elapsed_seconds": elapsed_seconds,
            })
            return

        stage_start = perf_counter()
        processor.load(input_file)
        stage_timings["Load time"] = _elapsed_since(stage_start)

        stage_start = perf_counter()
        repair.repair(processor.mesh)
        repair_stats = repair.statistics()
        stage_timings["Repair time"] = _elapsed_since(stage_start)
        logger.repair_statistics(repair_stats)
        logger.validation_statistics(repair_stats)

        stage_start = perf_counter()
        watertight_processor = WatertightProcessor(processor.mesh)
        processor.mesh = watertight_processor.repair()
        watertight_stats = watertight_processor.statistics()
        stage_timings["Watertight time"] = _elapsed_since(stage_start)
        logger.watertight_statistics(watertight_stats)

        # Preserve the repaired full-resolution mesh exactly as in v2.3.
        physical_source_mesh = copy.deepcopy(processor.mesh)
        source_watertight = GeometryUtils.is_watertight(
            physical_source_mesh
        )

        stage_start = perf_counter()
        processor.simplify()
        stage_timings["Simplification time"] = _elapsed_since(stage_start)

        optimized_watertight = GeometryUtils.is_watertight(processor.mesh)
        mesh_stats = processor.statistics()
        mesh_stats["watertight_physical_source"] = source_watertight
        mesh_stats["watertight_after_simplification"] = optimized_watertight
        logger.statistics(mesh_stats)

        physical_status = "FAILED"
        physical_method = "NOT CALCULATED"
        calculation_watertight = source_watertight
        calculation_mesh = None
        physical_stats = None
        convex_hull_mesh = None
        convex_hull_stats = None
        convex_hull_stl_path = None
        convex_hull_image_path = None

        def build_convex_hull(source_mesh):
            """Builds and validates a clean watertight Convex Hull."""
            hull = source_mesh.compute_convex_hull()[0]
            if hull.is_empty():
                raise ValueError("The convex hull generated an empty mesh.")
            if not hull.has_triangles():
                raise ValueError("The convex hull has no triangles.")

            hull.remove_duplicated_vertices()
            hull.remove_duplicated_triangles()
            hull.remove_degenerate_triangles()
            hull.remove_unreferenced_vertices()
            hull.compute_triangle_normals()
            hull.compute_vertex_normals()

            if not GeometryUtils.is_watertight(hull):
                raise ValueError("The generated convex hull is not watertight.")
            return hull

        stage_start = perf_counter()
        try:
            if source_watertight:
                calculation_mesh = physical_source_mesh
                physical_method = "EXACT REPAIRED MESH"
                physical_status = "SUCCESS"
            else:
                if not ENABLE_CONVEX_HULL_FALLBACK:
                    raise ValueError(
                        "The repaired mesh is not watertight and the "
                        "convex-hull fallback is disabled."
                    )

                convex_hull_mesh = build_convex_hull(physical_source_mesh)
                calculation_mesh = convex_hull_mesh
                calculation_watertight = True
                physical_method = "CONVEX HULL"
                physical_status = "APPROXIMATED"

            physical_stats = MassProcessor(calculation_mesh).calculate()
            calculation_completed = logger.physical_properties(
                physical_stats,
                method=physical_method,
                source_watertight=source_watertight,
                optimized_watertight=optimized_watertight,
                calculation_watertight=calculation_watertight,
                section_title=(
                    "5. Physical Properties - Exact Repaired Mesh"
                    if physical_method == "EXACT REPAIRED MESH"
                    else "5. Physical Properties - Convex Hull"
                ),
                role=(
                    "Primary exact calculation"
                    if physical_method == "EXACT REPAIRED MESH"
                    else "Fallback approximation"
                ),
            )
            if not calculation_completed:
                physical_status = "FAILED"

        except (ValueError, RuntimeError) as error:
            physical_status = "FAILED"
            logger.physical_properties_error(
                error,
                method=physical_method,
                source_watertight=source_watertight,
                optimized_watertight=optimized_watertight,
                calculation_watertight=calculation_watertight,
            )
        finally:
            stage_timings["Physical properties time"] = _elapsed_since(
                stage_start
            )

        # When the exact repaired mesh is valid, also calculate a separate
        # Convex Hull dataset for simulation/reference purposes. These
        # supplementary values never replace the exact physical properties.
        hull_properties_start = perf_counter()
        if physical_method == "EXACT REPAIRED MESH" and physical_stats is not None:
            try:
                convex_hull_mesh = build_convex_hull(physical_source_mesh)
                convex_hull_stats = MassProcessor(convex_hull_mesh).calculate()
                logger.physical_properties(
                    convex_hull_stats,
                    method="CONVEX HULL",
                    source_watertight=source_watertight,
                    optimized_watertight=optimized_watertight,
                    calculation_watertight=True,
                    section_title=(
                        "5.1 Supplementary Physical Properties - Convex Hull"
                    ),
                    role="Simulation/reference approximation",
                )
            except (ValueError, RuntimeError) as error:
                convex_hull_mesh = None
                convex_hull_stats = None
                logger.supplementary_physical_properties_error(error)
        elif physical_method == "CONVEX HULL" and physical_stats is not None:
            convex_hull_stats = physical_stats

        stage_timings["Convex Hull properties time"] = _elapsed_since(
            hull_properties_start
        )

        # The optimized STL is the primary result and is saved before any
        # auxiliary Convex Hull artifacts are attempted.
        stage_start = perf_counter()
        processor.save(output_path)
        logger.saved(output_path)
        stage_timings["STL export time"] = _elapsed_since(stage_start)

        # Generate Convex Hull artifacts whenever a valid hull exists,
        # regardless of whether it was used as fallback or as a supplementary
        # simulation/reference model.
        artifact_start = perf_counter()
        if convex_hull_mesh is not None and convex_hull_stats is not None:
            if SAVE_CONVEX_HULL_STL:
                try:
                    convex_hull_stl_path = (
                        file_manager.convex_hull_stl_path(input_file)
                    )
                    hull_exporter = MeshProcessor()
                    hull_exporter.mesh = convex_hull_mesh
                    hull_exporter.save(convex_hull_stl_path)
                    logger.artifact("Convex hull STL", convex_hull_stl_path)
                except Exception as error:
                    convex_hull_stl_path = None
                    logger.artifact_error("Convex hull STL", error)

            if SAVE_CONVEX_HULL_IMAGE:
                try:
                    from convex_hull_visualizer import ConvexHullVisualizer

                    convex_hull_image_path = (
                        file_manager.convex_hull_image_path(input_file)
                    )
                    ConvexHullVisualizer.save(
                        convex_hull_mesh,
                        convex_hull_image_path,
                        center_of_mass=convex_hull_stats.get(
                            "center_of_mass_model_units"
                        ),
                        title=(
                            f"{input_file.stem} - Convex Hull for "
                            "simulation/reference"
                        ),
                    )
                    logger.artifact(
                        "Convex hull image",
                        convex_hull_image_path,
                    )
                except Exception as error:
                    convex_hull_image_path = None
                    logger.artifact_error("Convex hull image", error)

        stage_timings["Artifact generation time"] = _elapsed_since(
            artifact_start
        )

        if physical_status == "SUCCESS":
            logger.set_result("SUCCESS", "SUCCESS", "SUCCESS")
            worker_status = "processed"
        elif physical_status == "APPROXIMATED":
            logger.set_result(
                "SUCCESS", "APPROXIMATED", "PARTIAL SUCCESS"
            )
            worker_status = "partial"
        else:
            logger.set_result("SUCCESS", "FAILED", "PARTIAL SUCCESS")
            worker_status = "partial"

        elapsed_seconds = _elapsed_since(worker_start_time)
        logger.set_stage_timings(stage_timings)
        logger.set_elapsed_time(elapsed_seconds)
        logger.summary()

        result_queue.put({
            "status": worker_status,
            "input_file": str(input_file),
            "output_file": str(output_path),
            "report_file": str(report_path),
            "physical_properties": physical_status,
            "elapsed_seconds": elapsed_seconds,
            "convex_hull_stl": (
                str(convex_hull_stl_path)
                if convex_hull_stl_path is not None else None
            ),
            "convex_hull_image": (
                str(convex_hull_image_path)
                if convex_hull_image_path is not None else None
            ),
        })

    except BaseException as error:
        try:
            logger.failure()
            logger.error(str(error))
            logger.message("")
            logger.message(traceback.format_exc())
            elapsed_seconds = _elapsed_since(worker_start_time)
            logger.set_stage_timings(stage_timings)
            logger.set_elapsed_time(elapsed_seconds)
            logger.summary()
        except Exception:
            traceback.print_exc()
            logger.close()

        try:
            result_queue.put({
                "status": "error",
                "input_file": str(input_file),
                "message": str(error),
                "elapsed_seconds": _elapsed_since(worker_start_time),
            })
        except Exception:
            pass
        raise


class STLOptimizer:
    """Coordinates all STL worker processes."""

    def __init__(self):
        self.file_manager = FileManager()
        self.processed = 0
        self.partially_processed = 0
        self.skipped = 0
        self.errors = 0
        self.timed_out = 0
        self.attempted_elapsed_seconds = []

    @staticmethod
    def _stop_process(process):
        if not process.is_alive():
            process.join()
            return
        process.terminate()
        process.join(TERMINATE_GRACE_SECONDS)
        if process.is_alive():
            process.kill()
            process.join()

    def _write_timeout_report(self, input_file, elapsed_seconds):
        timeout_logger = Logger()
        timeout_logger.log_file = self.file_manager.log_path(input_file)
        if not timeout_logger.log_file.exists():
            timeout_logger.start_log(timeout_logger.log_file)
            timeout_logger.begin_file(input_file.name)
        timeout_logger.timeout_summary(
            input_file.name,
            PROCESS_TIMEOUT_SECONDS,
            elapsed_seconds=elapsed_seconds,
        )

    def process_file_isolated(self, input_file):
        result_queue = mp.Queue(maxsize=1)
        process = mp.Process(
            target=process_stl_worker,
            args=(str(input_file), result_queue),
            name=f"STL-{input_file.stem}",
        )

        process_start_time = perf_counter()
        process.start()
        timeout = PROCESS_TIMEOUT_SECONDS if ENABLE_PROCESS_TIMEOUT else None
        process.join(timeout)

        if process.is_alive():
            self._stop_process(process)
            elapsed_seconds = _elapsed_since(process_start_time)
            self.attempted_elapsed_seconds.append(elapsed_seconds)
            self.timed_out += 1
            self.errors += 1
            self._write_timeout_report(input_file, elapsed_seconds)
            print(
                f"[TIMEOUT] '{input_file.name}' exceeded "
                f"{PROCESS_TIMEOUT_SECONDS} seconds. "
                "Continuing with the next STL."
            )
            result_queue.close()
            result_queue.join_thread()
            return

        result = None
        try:
            result = result_queue.get(timeout=1.0)
        except queue.Empty:
            pass
        finally:
            result_queue.close()
            result_queue.join_thread()

        if result is not None:
            status = result.get("status")
            elapsed_seconds = result.get("elapsed_seconds")
            if status != "skipped" and elapsed_seconds is not None:
                try:
                    self.attempted_elapsed_seconds.append(
                        max(0.0, float(elapsed_seconds))
                    )
                except (TypeError, ValueError):
                    pass

            if status == "processed":
                self.processed += 1
            elif status == "partial":
                self.partially_processed += 1
            elif status == "skipped":
                self.skipped += 1
            else:
                self.errors += 1
            return

        self.attempted_elapsed_seconds.append(
            _elapsed_since(process_start_time)
        )
        self.errors += 1
        if process.exitcode != 0:
            print(
                f"[ERROR] '{input_file.name}' worker exited "
                f"with code {process.exitcode}."
            )
        else:
            print(
                f"[ERROR] '{input_file.name}' finished without "
                "returning a processing result."
            )

    def run(self):
        batch_start_time = perf_counter()

        # Search exactly once and reuse the same ordered list throughout
        # the complete batch.
        files = self.file_manager.stl_files()

        print("-" * 60)
        print("STL OPTIMIZER")
        print("-" * 60)
        print(f"Working directory : {self.file_manager.working_directory()}")
        print(f"Recursive search  : {SEARCH_SUBDIRECTORIES}")
        print(f"Files found       : {len(files)}")
        print(f"Timeout enabled   : {ENABLE_PROCESS_TIMEOUT}")
        if ENABLE_PROCESS_TIMEOUT:
            print(f"Timeout per STL   : {PROCESS_TIMEOUT_SECONDS} seconds")
        print("-" * 60)

        if not files:
            print("[ERROR] No STL files were found.")
            return

        for index, input_file in enumerate(files, start=1):
            print(f"\n[{index}/{len(files)}] Processing '{input_file.name}'")
            self.process_file_isolated(input_file)

        batch_elapsed_seconds = _elapsed_since(batch_start_time)
        print("\n" + "-" * 60)
        print("BATCH SUMMARY")
        print("-" * 60)
        print(f"Successfully processed : {self.processed}")
        print(f"Partially processed    : {self.partially_processed}")
        print(f"Skipped                : {self.skipped}")
        print(f"Timed out              : {self.timed_out}")
        print(f"Errors                 : {self.errors}")
        print(
            "Total execution time   : "
            f"{format_elapsed_time(batch_elapsed_seconds)}"
        )
        print(f"Total seconds          : {batch_elapsed_seconds:.3f}")

        if self.attempted_elapsed_seconds:
            average_seconds = (
                sum(self.attempted_elapsed_seconds)
                / len(self.attempted_elapsed_seconds)
            )
            print(
                "Average time per STL  : "
                f"{format_elapsed_time(average_seconds)}"
            )
            print(f"Average seconds/STL   : {average_seconds:.3f}")
        else:
            print("Average time per STL  : NOT AVAILABLE")
            print("Average seconds/STL   : NOT AVAILABLE")
        print("-" * 60)


if __name__ == "__main__":
    mp.freeze_support()
    mp.set_start_method("spawn", force=True)
    STLOptimizer().run()
