"""
=========================================================
STL OPTIMIZER

Repair Processor

Repairs and validates STL meshes before optimization.

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

import open3d as o3d


class RepairProcessor:
    """
    Repairs a mesh before simplification and
    stores information about every correction made.
    """

    # ---------------------------------------------------------

    def __init__(self):

        self.reset()

    # ---------------------------------------------------------

    def reset(self):

        self.duplicated_vertices_removed = 0

        self.duplicated_triangles_removed = 0

        self.degenerate_triangles_removed = 0

        self.non_manifold_edges_removed = 0

        self.unreferenced_vertices_removed = 0

        self.normals_recomputed = False

        # -------------------------------------------------
        # Mesh validation
        # -------------------------------------------------

        self.is_empty = None

        self.is_edge_manifold = None

        self.is_vertex_manifold = None

        self.is_watertight = None

        self.is_orientable = None

        self.is_self_intersecting = None

        self.repaired = False

        self.has_triangles = False

    # ---------------------------------------------------------

    def _safe_check(self, function):
        """
        Safely executes any validation function.

        If the validation is not supported or raises an
        exception, "Not supported" is returned.
        """

        try:
            return function()

        except Exception:
            return "Not supported"

    # ---------------------------------------------------------

    def repair(self, mesh):
        """
        Repairs a mesh and returns the repaired mesh.
        """

        self.reset()

        self.mesh = mesh

        # ---------------------------------------------
        # Duplicated vertices
        # ---------------------------------------------

        before = len(self.mesh.vertices)

        self.mesh.remove_duplicated_vertices()

        after = len(self.mesh.vertices)

        self.duplicated_vertices_removed = before - after

        # ---------------------------------------------
        # Duplicated triangles
        # ---------------------------------------------

        before = len(self.mesh.triangles)

        self.mesh.remove_duplicated_triangles()

        after = len(self.mesh.triangles)

        self.duplicated_triangles_removed = before - after

        # ---------------------------------------------
        # Degenerated triangles
        # ---------------------------------------------

        before = len(self.mesh.triangles)

        self.mesh.remove_degenerate_triangles()

        after = len(self.mesh.triangles)

        self.degenerate_triangles_removed = before - after

        # ---------------------------------------------
        # Non-manifold edges
        # ---------------------------------------------

        before = len(self.mesh.triangles)

        self.mesh.remove_non_manifold_edges()

        after = len(self.mesh.triangles)

        self.non_manifold_edges_removed = before - after

        # ---------------------------------------------
        # Unreferenced vertices
        # ---------------------------------------------

        before = len(self.mesh.vertices)

        self.mesh.remove_unreferenced_vertices()

        after = len(self.mesh.vertices)

        self.unreferenced_vertices_removed = before - after

        # ---------------------------------------------
        # Recompute normals
        # ---------------------------------------------

        self.mesh.compute_vertex_normals()

        self.normals_recomputed = True

        # ---------------------------------------------
        # Was anything repaired?
        # ---------------------------------------------

        self.repaired = any([
            self.duplicated_vertices_removed,
            self.duplicated_triangles_removed,
            self.degenerate_triangles_removed,
            self.non_manifold_edges_removed,
            self.unreferenced_vertices_removed
        ])

        # ---------------------------------------------
        # Mesh validation
        # ---------------------------------------------

        self.is_empty = self._safe_check(
            self.mesh.is_empty
        )

        self.has_triangles = self._safe_check(
            lambda: len(self.mesh.triangles) > 0
        )

        self.is_edge_manifold = self._safe_check(
            self.mesh.is_edge_manifold
        )

        self.is_vertex_manifold = self._safe_check(
            self.mesh.is_vertex_manifold
        )

        self.is_watertight = self._safe_check(
            self.mesh.is_watertight
        )

        self.is_orientable = self._safe_check(
            self.mesh.is_orientable
        )

        self.is_self_intersecting = self._safe_check(
            self.mesh.is_self_intersecting
        )
    
    # ---------------------------------------------------------

    def statistics(self):
        """
        Returns repair and validation statistics.
        """

        return {

            # -----------------------------
            # Repair
            # -----------------------------

            "mesh_repaired":
                self.repaired,

            "duplicated_vertices":
                self.duplicated_vertices_removed,

            "duplicated_triangles":
                self.duplicated_triangles_removed,

            "degenerate_triangles":
                self.degenerate_triangles_removed,

            "non_manifold_edges":
                self.non_manifold_edges_removed,

            "unreferenced_vertices":
                self.unreferenced_vertices_removed,

            "normals_recomputed":
                self.normals_recomputed,

            # -----------------------------
            # Validation
            # -----------------------------

            "is_empty":
                self.is_empty,

            "has_triangles":
                self.has_triangles,

            "edge_manifold":
                self.is_edge_manifold,

            "vertex_manifold":
                self.is_vertex_manifold,

            "watertight":
                self.is_watertight,

            "orientable":
                self.is_orientable,

            "self_intersections":
                self.is_self_intersecting
        }