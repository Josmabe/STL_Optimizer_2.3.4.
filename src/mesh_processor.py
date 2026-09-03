"""
=========================================================
STL OPTIMIZER

Mesh Processor

Process and optimize STL meshes using Open3D.

Compatible con:
    - Windows
    - Linux
    - SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

import os
from pathlib import Path
import open3d as o3d

from config_API import (
    SimplificationMode,
    SIMPLIFICATION_MODE,
    TARGET_TRIANGLES,
    KEEP_PERCENTAGE,
    REMOVE_DUPLICATED_VERTICES,
    REMOVE_DUPLICATED_TRIANGLES,
    REMOVE_DEGENERATED_TRIANGLES,
    REMOVE_NON_MANIFOLD_EDGES,
    OUTPUT_SUFFIX,
    OVERWRITE_EXISTING
)


class MeshProcessor:
    """
    Class responsible for loading, cleaning, simplifying, and saving
    STL models using Open3D.
    """

    # ---------------------------------------------------------

    def __init__(self):

        self.mesh = None
        self.filename = None

        self.original_vertices = 0
        self.original_triangles = 0

        self.final_vertices = 0
        self.final_triangles = 0

        # Indicates whether normals have been recomputed
        # after the simplification process.
        self.normals_recomputed_after_simplification = False

    # ---------------------------------------------------------

    def _update_statistics(self):
        """
        Updates the number of vertices and triangles
        of the currently loaded mesh.
        """

        if self.mesh is None:
            return

        self.final_vertices = len(self.mesh.vertices)
        self.final_triangles = len(self.mesh.triangles)

    # ---------------------------------------------------------

    def load(self, filename):
        """
        Upload an STL file.
        """

        filename = Path(filename)

        self.filename = filename

        self.normals_recomputed_after_simplification = False

        # ---------------------------------------------------------
        # Check for non-ASCII characters in the path.
        #
        # Some Windows builds of Open3D cannot read STL files whose
        # path contains accented or non-ASCII characters.
        # ---------------------------------------------------------

        try:
            str(filename).encode("ascii")

        except UnicodeEncodeError:

            raise RuntimeError(
                "\n"
                "Open3D cannot read STL files from paths containing "
                "accented or special characters.\n\n"
                f"Current path:\n{filename}\n\n"
                "Please move the project to a folder whose path "
                "contains only standard English characters."
            )

        # ---------------------------------------------------------

        try:

            self.mesh = o3d.io.read_triangle_mesh(str(filename))

        except UnicodeDecodeError:

            raise RuntimeError(
                "\n"
                "Open3D failed to read the STL file.\n\n"
                "This is usually caused by a file path containing "
                "accented or non-ASCII characters.\n\n"
                f"Current path:\n{filename}"
            )
        
        if self.mesh.is_empty():
            raise RuntimeError(
                f"'{filename}' It does not contain geometry."
            )

        if len(self.mesh.triangles) == 0:
            raise RuntimeError(
                f"'{filename}' it does not contain triangles."
            )

        #self.mesh.compute_vertex_normals()

        self.original_vertices = len(self.mesh.vertices)
        self.original_triangles = len(self.mesh.triangles)

        self._update_statistics()

    # ---------------------------------------------------------
    """
    def clean(self):
        
        # Cleans the mesh by removing redundant geometry.
        

        if REMOVE_DUPLICATED_VERTICES:
            self.mesh.remove_duplicated_vertices()

        if REMOVE_DUPLICATED_TRIANGLES:
            self.mesh.remove_duplicated_triangles()

        if REMOVE_DEGENERATED_TRIANGLES:
            self.mesh.remove_degenerate_triangles()

        if REMOVE_NON_MANIFOLD_EDGES:
            self.mesh.remove_non_manifold_edges()

        self.mesh.remove_unreferenced_vertices()

        self.mesh.compute_vertex_normals()

        self._update_statistics()
    """

    # ---------------------------------------------------------

    def _target_triangle_count(self):
        """
        Calculate the target number of triangles
        based on the selected configuration.
        """

        if SIMPLIFICATION_MODE == SimplificationMode.TARGET_TRIANGLES:

            target = TARGET_TRIANGLES

        else:

            target = int(
                self.original_triangles *
                KEEP_PERCENTAGE
            )

        target = max(4, target)

        target = min(
            target,
            self.original_triangles
        )

        return target

    # ---------------------------------------------------------

    def simplify(self):
        """
        Simplify the mesh using Quadric Error Metrics.
        """

        target = self._target_triangle_count()

        self.mesh = self.mesh.simplify_quadric_decimation(
            target_number_of_triangles=target
        )
        
        self.mesh.remove_unreferenced_vertices()

        self.mesh.compute_vertex_normals()

        self.normals_recomputed_after_simplification = True

        self._update_statistics()
    
        # ---------------------------------------------------------

    def reduction_percent(self):
        """
        Returns the triangle reduction percentage.
        """

        if self.original_triangles == 0:
            return 0.0

        reduction = (
            1.0
            - (
                self.final_triangles
                / self.original_triangles
            )
        ) * 100.0

        return reduction

    # ---------------------------------------------------------

    def statistics(self):
        """
        Returns the mesh statistics.
        """

        return {
        "original_vertices": self.original_vertices,
        "original_triangles": self.original_triangles,
        "final_vertices": self.final_vertices,
        "final_triangles": self.final_triangles,
        "reduction": self.reduction_percent(),

        "normals_recomputed_after_simplification":
            self.normals_recomputed_after_simplification
        }   

    # ---------------------------------------------------------

    def save(self, output_file):
        """Saves a mesh atomically to avoid incomplete final files."""
        output_file = Path(output_file)

        if self.mesh is None:
            raise RuntimeError("There is no loaded mesh.")
        if self.mesh.is_empty():
            raise RuntimeError(
                "The loaded mesh is empty and cannot be saved."
            )
        if len(self.mesh.triangles) == 0:
            raise RuntimeError(
                "The loaded mesh has no triangles and cannot be saved."
            )

        output_file.parent.mkdir(parents=True, exist_ok=True)
        temporary_file = output_file.with_name(
            f".{output_file.stem}.tmp{output_file.suffix}"
        )

        try:
            success = o3d.io.write_triangle_mesh(
                str(temporary_file),
                self.mesh,
                write_ascii=False,
                compressed=False,
                write_vertex_normals=True,
                write_vertex_colors=False,
                write_triangle_uvs=False,
            )

            if not success:
                raise RuntimeError(
                    f"'{output_file.name}' could not be saved."
                )
            if not temporary_file.exists() or temporary_file.stat().st_size == 0:
                raise RuntimeError(
                    f"'{output_file.name}' was written as an empty file."
                )

            os.replace(temporary_file, output_file)
        finally:
            if temporary_file.exists():
                try:
                    temporary_file.unlink()
                except OSError:
                    pass

        return output_file

    # ---------------------------------------------------------

    def filename(self):
        return self.filename.name