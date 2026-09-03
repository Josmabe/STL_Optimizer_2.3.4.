"""
=========================================================
STL OPTIMIZER

Logger

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

from datetime import datetime
from pathlib import Path

from config_API import SAVE_LOG_FILE, VERBOSE
from time_utils import format_elapsed_time


class Logger:

    @staticmethod
    def _format_inertia_row(row):
        return (
            f"[ "
            f"{float(row[0]): .12e}  "
            f"{float(row[1]): .12e}  "
            f"{float(row[2]): .12e} "
            f"]"
        )

    @staticmethod
    def _format_check(value):
        """Formats validation values without converting errors to YES."""

        if value is True:
            return "YES"

        if value is False:
            return "NO"

        if value is None:
            return "NOT CHECKED"

        return str(value).upper()

    # ---------------------------------------------------------

    def __init__(self):
        self.log_file = None
        self._file_handle = None
        self.output_files = []
        self.artifacts = []

        self.optimization_status = "NOT STARTED"
        self.physical_properties_status = "NOT CALCULATED"
        self.overall_status = "NOT STARTED"

        self.processed = 0
        self.partially_processed = 0
        self.failed = 0
        self.elapsed_seconds = None
        self.stage_timings = {}

    # ---------------------------------------------------------

    def start_log(self, log_path):
        self.close()
        self.log_file = Path(log_path)
        self.output_files = []
        self.artifacts = []

        self.optimization_status = "NOT STARTED"
        self.physical_properties_status = "NOT CALCULATED"
        self.overall_status = "NOT STARTED"

        self.processed = 0
        self.partially_processed = 0
        self.failed = 0
        self.elapsed_seconds = None
        self.stage_timings = {}

        if SAVE_LOG_FILE:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self._file_handle = open(
                self.log_file,
                "w",
                encoding="utf-8",
                buffering=1,
            )
            self._file_handle.write(
                "============================================================\n"
                "                 STL OPTIMIZER REPORT\n"
                "============================================================\n"
                f"\nStarted : {datetime.now()}\n\n"
            )
            self._file_handle.flush()

    # ---------------------------------------------------------

    def _write(self, text):
        if VERBOSE:
            print(text)

        if not SAVE_LOG_FILE or self.log_file is None:
            return

        if self._file_handle is not None:
            self._file_handle.write(text + "\n")
            self._file_handle.flush()
            return

        # Fallback used by the parent process when completing a
        # report after a timeout.
        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(text + "\n")
            file.flush()

    def close(self):
        """Flushes and closes the report file if it is open."""
        if self._file_handle is not None:
            try:
                self._file_handle.flush()
            finally:
                self._file_handle.close()
                self._file_handle = None

    # ---------------------------------------------------------

    def field(self, name, value):
        self._write(f"{name:.<40} {value}")

    def separator(self):
        self._write("-" * 60)

    def title(self, text):
        self.separator()
        self._write(text)
        self.separator()

    def begin_file(self, filename):
        self.separator()
        self._write(f"Processing STL : {filename}")
        self.separator()

    def message(self, text):
        self._write(text)

    def error(self, text):
        self._write(f"[ERROR] {text}")

    def artifact_error(self, label, error):
        """Reports a non-fatal auxiliary artifact failure."""
        self._write(f"[WARNING] {label} could not be generated: {error}")

    # ---------------------------------------------------------
    # PROCESS RESULT STATUS
    # ---------------------------------------------------------

    def set_result(
        self,
        optimization,
        physical_properties,
        overall,
    ):
        """Stores the final status values shown in section 6."""

        self.optimization_status = str(optimization).upper()
        self.physical_properties_status = str(
            physical_properties
        ).upper()
        self.overall_status = str(overall).upper()

        self.processed = 0
        self.partially_processed = 0
        self.failed = 0

        if self.overall_status == "SUCCESS":
            self.processed = 1
        elif self.overall_status == "PARTIAL SUCCESS":
            self.partially_processed = 1
        else:
            self.failed = 1

    # Compatibility methods used by older code.
    def success(self):
        self.set_result("SUCCESS", "SUCCESS", "SUCCESS")

    def partial_success(self, physical_status="FAILED"):
        self.set_result(
            "SUCCESS",
            physical_status,
            "PARTIAL SUCCESS",
        )

    def failure(self):
        self.set_result("FAILED", "NOT CALCULATED", "FAILED")

    # ---------------------------------------------------------

    def set_elapsed_time(self, elapsed_seconds):
        """Stores the elapsed processing time for this STL."""

        try:
            self.elapsed_seconds = max(0.0, float(elapsed_seconds))
        except (TypeError, ValueError):
            self.elapsed_seconds = None

    def set_stage_timings(self, timings):
        """Stores optional per-stage elapsed times."""
        self.stage_timings = {}
        for name, seconds in (timings or {}).items():
            try:
                self.stage_timings[str(name)] = max(0.0, float(seconds))
            except (TypeError, ValueError):
                continue

    # ---------------------------------------------------------

    def repair_statistics(self, stats):
        self._write("")
        self._write("1. Mesh repair")
        self._write("-------------------------")
        self.field(
            "Repairs applied",
            "YES" if stats["mesh_repaired"] else "NO",
        )
        self.field("Duplicated vertices", stats["duplicated_vertices"])
        self.field("Duplicated triangles", stats["duplicated_triangles"])
        self.field("Degenerate triangles", stats["degenerate_triangles"])
        self.field("Non-manifold edges", stats["non_manifold_edges"])
        self.field("Unused vertices", stats["unreferenced_vertices"])
        self.field(
            "Normals after repair",
            "YES" if stats["normals_recomputed"] else "NO",
        )
        self._write("")

    # ---------------------------------------------------------

    def validation_statistics(self, stats):
        self._write("")
        self._write("2. Mesh validation")
        self._write("-------------------------")
        self.field(
            "Is empty",
            self._format_check(stats["is_empty"]),
        )
        self.field(
            "Has triangles",
            self._format_check(stats["has_triangles"]),
        )
        self.field(
            "Is edge manifold",
            self._format_check(stats["edge_manifold"]),
        )
        self.field(
            "Is vertex manifold",
            self._format_check(stats["vertex_manifold"]),
        )
        self.field(
            "Is watertight",
            self._format_check(stats["watertight"]),
        )
        self.field(
            "Is orientable",
            self._format_check(stats["orientable"]),
        )
        self.field(
            "Self intersections",
            self._format_check(stats["self_intersections"]),
        )
        self._write("")

    # ---------------------------------------------------------

    def watertight_statistics(self, stats):
        self._write("")
        self._write("3. Watertight repair")
        self._write("-------------------------")
        self.field(
            "Input watertight",
            "YES" if stats["input_watertight"] else "NO",
        )
        self.field("Holes repaired", stats["holes_repaired"])
        self.field("Faces added", stats["faces_added"])
        self.field(
            "Output watertight",
            "YES" if stats["output_watertight"] else "NO",
        )
        self._write("")

    # ---------------------------------------------------------

    def statistics(self, stats):
        self._write("")
        self._write("4. Mesh statistics")
        self._write("-------------------------")
        self.field("Original vertices", stats["original_vertices"])
        self.field("Optimized vertices", stats["final_vertices"])
        self.field("Original triangles", stats["original_triangles"])
        self.field("Optimized triangles", stats["final_triangles"])
        self.field("Reduction of triangles", f"{stats['reduction']:.2f} %")
        self.field(
            "Normals after simplification",
            "YES"
            if stats["normals_recomputed_after_simplification"]
            else "NO",
        )

        if "watertight_physical_source" in stats:
            self.field(
                "Repaired source watertight",
                self._format_check(
                    stats["watertight_physical_source"]
                ),
            )

        if "watertight_after_simplification" in stats:
            self.field(
                "Optimized STL watertight",
                self._format_check(
                    stats["watertight_after_simplification"]
                ),
            )

        self._write("")

    # ---------------------------------------------------------

    def saved(self, filename):
        output_file = Path(filename)

        if output_file not in self.output_files:
            self.output_files.append(output_file)

    # ---------------------------------------------------------

    def artifact(self, label, filename):
        """Registers an additional generated output artifact."""

        path = Path(filename)
        item = (str(label), path)
        if item not in self.artifacts:
            self.artifacts.append(item)

    # ---------------------------------------------------------

    # ---------------------------------------------------------

    def physical_properties(
        self,
        statistics,
        method="EXACT MESH",
        source_watertight=None,
        optimized_watertight=None,
        calculation_watertight=None,
        section_title="5. Physical Properties",
        role=None,
    ):
        """
        Writes physical properties and returns True when the
        supplied calculation is complete.

        The optional method field is ready for the future
        CONVEX HULL fallback.
        """

        self._write("")
        self._write(section_title)
        self._write("-------------------------")
        self.field("Calculation method", method)
        if role is not None:
            self.field("Calculation role", role)

        if source_watertight is not None:
            self.field(
                "Repaired source watertight",
                "YES" if source_watertight else "NO",
            )

        if optimized_watertight is not None:
            self.field(
                "Optimized STL watertight",
                "YES" if optimized_watertight else "NO",
            )

        if calculation_watertight is not None:
            label = (
                "Approximation watertight"
                if str(method).upper() == "CONVEX HULL"
                else "Calculation mesh watertight"
            )
            self.field(
                label,
                "YES" if calculation_watertight else "NO",
            )

        if str(method).upper() == "CONVEX HULL":
            self.field("Approximation used", "YES")

        if statistics is None:
            self.error(
                "Physical property statistics are not available."
            )
            self._write("")
            return False

        if not statistics.get("calculation_completed", False):
            self.error(
                "Physical property calculation was not completed."
            )
            self._write("")
            return False

        mass_kg = statistics.get("mass_kg")
        volume_m3 = statistics.get("volume_m3")
        density_kg_m3 = statistics.get("density_kg_m3")
        center_of_mass = statistics.get("center_of_mass_m")
        inertia_tensor = statistics.get("inertia_tensor_kg_m2")

        if mass_kg is None:
            self.error("The calculated mass is not available.")
            self._write("")
            return False

        if center_of_mass is None:
            self.error("The center of mass is not available.")
            self._write("")
            return False

        if inertia_tensor is None:
            self.error("The inertia tensor is not available.")
            self._write("")
            return False

        self._write(f"Mass............................{mass_kg:.9f} kg")

        if volume_m3 is not None:
            self._write(
                f"Volume..........................{volume_m3:.12e} m³"
            )

        if density_kg_m3 is not None:
            self._write(
                "Equivalent density.............."
                f"{density_kg_m3:.6f} kg/m³"
            )

        self._write("")
        self._write("Center of mass [m]:")
        self._write(
            f"X...............................{center_of_mass[0]: .9f} m"
        )
        self._write(
            f"Y...............................{center_of_mass[1]: .9f} m"
        )
        self._write(
            f"Z...............................{center_of_mass[2]: .9f} m"
        )

        self._write("")
        self._write("Inertia tensor [kg·m²]:")
        self._write("")
        self._write(self._format_inertia_row(inertia_tensor[0]))
        self._write(self._format_inertia_row(inertia_tensor[1]))
        self._write(self._format_inertia_row(inertia_tensor[2]))
        self._write("")

        return True


    # ---------------------------------------------------------


    def supplementary_physical_properties_error(self, error):
        """Reports failure of the optional Convex Hull comparison block."""
        self._write("")
        self._write("5.1 Supplementary Physical Properties - Convex Hull")
        self._write("-------------------------")
        self.field("Calculation method", "CONVEX HULL")
        self.field("Calculation role", "Simulation/reference approximation")
        self.error(str(error))
        self._write("")

    # ---------------------------------------------------------
    def physical_properties_error(
        self,
        error,
        method="NOT CALCULATED",
        source_watertight=None,
        optimized_watertight=None,
        calculation_watertight=None,
    ):
        """Writes a complete section 5 when calculation fails."""

        self._write("")
        self._write("5. Physical Properties")
        self._write("-------------------------")
        self.field("Calculation method", method)

        if source_watertight is not None:
            self.field(
                "Repaired source watertight",
                "YES" if source_watertight else "NO",
            )

        if optimized_watertight is not None:
            self.field(
                "Optimized STL watertight",
                "YES" if optimized_watertight else "NO",
            )

        if calculation_watertight is not None:
            self.field(
                "Calculation mesh watertight",
                "YES" if calculation_watertight else "NO",
            )

        self.error(
            "Physical properties could not be calculated: "
            f"{error}"
        )
        self._write("")

    # ---------------------------------------------------------

    def summary(self):
        self._write("")
        self._write("6. Process Summary")
        self._write("-------------------------")

        self.field("Optimization", self.optimization_status)
        self.field(
            "Physical properties",
            self.physical_properties_status,
        )
        self.field("Overall result", self.overall_status)

        self._write("")
        self.field("Successfully processed", self.processed)
        self.field(
            "Partially processed",
            self.partially_processed,
        )
        self.field("Errors", self.failed)

        if self.output_files:
            self._write("")

            for index, output_file in enumerate(
                self.output_files,
                start=1,
            ):
                field_name = (
                    "Output STL"
                    if len(self.output_files) == 1
                    else f"Output STL {index}"
                )
                self.field(field_name, str(output_file))

        if self.artifacts:
            self._write("")
            for label, artifact_path in self.artifacts:
                self.field(label, str(artifact_path))

        if self.log_file is not None:
            self.field("Output report", str(self.log_file))

        if self.stage_timings:
            self._write("")
            self._write("Stage timings")
            self._write("-------------------------")
            for stage_name, stage_seconds in self.stage_timings.items():
                self.field(
                    stage_name,
                    f"{format_elapsed_time(stage_seconds)} "
                    f"({stage_seconds:.3f} s)",
                )

        if self.elapsed_seconds is not None:
            self._write("")
            self.field(
                "Processing time",
                format_elapsed_time(self.elapsed_seconds),
            )
            self.field(
                "Processing seconds",
                f"{self.elapsed_seconds:.3f}",
            )

        self.field("Finished", datetime.now())
        self._write("")
        self._write("End of report.")
        self.close()

    # ---------------------------------------------------------

    def timeout_summary(
        self,
        filename,
        timeout_seconds,
        elapsed_seconds=None,
    ):
        self.error(
            f"Processing timeout: '{filename}' exceeded "
            f"{timeout_seconds} seconds."
        )
        self.set_result("FAILED", "NOT CALCULATED", "FAILED")

        if elapsed_seconds is not None:
            self.set_elapsed_time(elapsed_seconds)

        self.summary()
