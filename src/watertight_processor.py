"""
=========================================================
STL OPTIMIZER

Watertight Processor

Attempts to convert an open triangular mesh into a
watertight mesh using conservative repair operations.

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

from geometry_utils import GeometryUtils


class WatertightProcessor:
    """
    Attempts to make an Open3D TriangleMesh watertight.

    This processor uses Trimesh internally because Trimesh
    provides operations specifically designed for repairing
    triangular surfaces.

    The current implementation is intentionally conservative.
    It attempts to:

        1. Correct face winding.
        2. Correct face normals.
        3. Fill small triangular or quadrilateral holes.
        4. Remove unreferenced vertices.
        5. Convert the result back to Open3D.

    This processor does not use voxel reconstruction or
    remeshing. Therefore, it should not significantly alter
    the original geometry.

    Notes
    -----
    Trimesh's standard hole-filling method is mainly intended
    for small holes composed of one triangle or one
    quadrilateral.

    Large openings, self-intersections or heavily damaged
    meshes may require a more aggressive reconstruction method.
    """

    # ---------------------------------------------------------

    def __init__(self, mesh):
        """
        Initializes the watertight processor.

        Parameters
        ----------
        mesh : open3d.geometry.TriangleMesh
            Open3D mesh that will be processed.
        """

        self.mesh = mesh

        self.was_watertight_before = False
        self.is_watertight_after = False

        self.repair_attempted = False
        self.repair_successful = False

        self.faces_before = 0
        self.faces_after = 0
        self.faces_added = 0

        self.vertices_before = 0
        self.vertices_after = 0

        self.normals_fixed = False
        self.holes_fill_attempted = False
        self.holes_repaired = False

    # ---------------------------------------------------------

    def _validate_mesh(self):
        """
        Validates that the input mesh can be processed.

        Raises
        ------
        ValueError
            If the mesh is None, empty or contains no
            triangular faces.
        """

        if self.mesh is None:

            raise ValueError(
                "The mesh cannot be None."
            )

        if self.mesh.is_empty():

            raise ValueError(
                "The mesh cannot be made watertight "
                "because it is empty."
            )

        if len(self.mesh.triangles) == 0:

            raise ValueError(
                "The mesh cannot be made watertight "
                "because it has no triangles."
            )

    # ---------------------------------------------------------

    def repair(self):
        """
        Attempts to make the mesh watertight.

        Returns
        -------
        open3d.geometry.TriangleMesh
            Repaired Open3D mesh.

        Notes
        -----
        The returned mesh must be assigned back to the
        corresponding MeshProcessor because the conversion
        creates a new Open3D TriangleMesh object.
        """

        self._validate_mesh()

        trimesh_mesh = GeometryUtils.open3d_to_trimesh(
            self.mesh
        )

        self.vertices_before = len(
            trimesh_mesh.vertices
        )

        self.faces_before = len(
            trimesh_mesh.faces
        )

        self.was_watertight_before = bool(
            trimesh_mesh.is_watertight
        )

        # No repair is required if the mesh is already closed.
        if self.was_watertight_before:

            self.is_watertight_after = True
            self.repair_successful = True

            self.vertices_after = (
                self.vertices_before
            )

            self.faces_after = (
                self.faces_before
            )

            self.faces_added = 0
            self.holes_repaired = False

            return self.mesh

        self.repair_attempted = True

        # Correct face winding and normal orientation.
        trimesh_mesh.fix_normals(
            multibody=True
        )

        self.normals_fixed = True

        # Attempt to close small triangular or quadrilateral
        # holes in the surface.
        self.holes_fill_attempted = True

        faces_before_fill = len(
            trimesh_mesh.faces
        )

        fill_result = trimesh_mesh.fill_holes()

        faces_after_fill = len(
            trimesh_mesh.faces
        )

        faces_added_by_fill = max(
            0,
            faces_after_fill - faces_before_fill
        )

        self.holes_repaired = (
            faces_added_by_fill > 0
        )

        # Remove vertices that are no longer referenced by
        # any triangular face.
        trimesh_mesh.remove_unreferenced_vertices()

        self.vertices_after = len(
            trimesh_mesh.vertices
        )

        self.faces_after = len(
            trimesh_mesh.faces
        )

        self.faces_added = max(
            0,
            self.faces_after - self.faces_before
        )

        self.is_watertight_after = bool(
            trimesh_mesh.is_watertight
        )

        self.repair_successful = (
            self.is_watertight_after
        )

        # fill_holes() returns the watertight state after the
        # operation. The final state is checked again after
        # removing unreferenced vertices.
        if fill_result and not self.is_watertight_after:

            self.repair_successful = False

        self.mesh = GeometryUtils.trimesh_to_open3d(
            trimesh_mesh
        )

        return self.mesh

    # ---------------------------------------------------------

    def statistics(self):
        """
        Returns statistics about the watertight repair.

        Returns
        -------
        dict
            Dictionary containing the watertight state before
            and after processing, together with information
            about the repair operations.
        """

        return {
            # Keys used directly by Logger.
            "input_watertight":
                self.was_watertight_before,

            "holes_repaired":
                self.holes_repaired,

            "faces_added":
                self.faces_added,

            "output_watertight":
                self.is_watertight_after,

            # Additional diagnostic information.
            "repair_attempted":
                self.repair_attempted,

            "normals_fixed":
                self.normals_fixed,

            "hole_filling_attempted":
                self.holes_fill_attempted,

            "faces_before":
                self.faces_before,

            "faces_after":
                self.faces_after,

            "vertices_before":
                self.vertices_before,

            "vertices_after":
                self.vertices_after,

            "repair_successful":
                self.repair_successful
        }