"""
=========================================================
STL OPTIMIZER

Geometry Utilities

Utility functions for geometry processing.

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

import numpy as np
import open3d as o3d
import trimesh


class GeometryUtils:
    """
    Utility functions shared by different processors.

    This class centralizes conversions between geometry
    libraries and common geometric calculations.
    """

    # ---------------------------------------------------------

    @staticmethod
    def open3d_to_trimesh(mesh):
        """
        Converts an Open3D TriangleMesh into a Trimesh object.
        """

        vertices = np.asarray(mesh.vertices)

        triangles = np.asarray(mesh.triangles)

        trimesh_mesh = trimesh.Trimesh(
            vertices=vertices,
            faces=triangles,
            process=False
        )

        return trimesh_mesh

    # ---------------------------------------------------------

    @staticmethod
    def trimesh_to_open3d(mesh):
        """
        Converts a Trimesh object into an Open3D TriangleMesh.
        """

        o3d_mesh = o3d.geometry.TriangleMesh()

        o3d_mesh.vertices = o3d.utility.Vector3dVector(
            mesh.vertices
        )

        o3d_mesh.triangles = o3d.utility.Vector3iVector(
            mesh.faces
        )

        o3d_mesh.compute_vertex_normals()

        return o3d_mesh
    
    # ---------------------------------------------------------

    @staticmethod
    def is_watertight(mesh):
        """
        Checks whether a triangular mesh encloses a closed volume.

        Trimesh is used here so the same watertight criterion is
        applied by the main program and by MassProcessor. This avoids
        selecting CONVEX HULL merely because Open3D applies a stricter
        diagnostic after quadric decimation.
        """

        if mesh is None or mesh.is_empty() or len(mesh.triangles) == 0:
            return False

        trimesh_mesh = GeometryUtils.open3d_to_trimesh(mesh)
        return bool(trimesh_mesh.is_watertight)

    # ---------------------------------------------------------

    @staticmethod
    def bounding_box(mesh):
        """
        Returns the axis-aligned bounding box.
        """

        return mesh.get_axis_aligned_bounding_box()
    
    # ---------------------------------------------------------

    @staticmethod
    def center(mesh):
        """
        Returns the geometric center of the mesh.
        """

        return mesh.get_center()
    
    # ---------------------------------------------------------

    @staticmethod
    def dimensions(mesh):
        """
        Returns the dimensions of the mesh.

        Returns
        -------
        (width, height, depth)
        """

        bbox = mesh.get_axis_aligned_bounding_box()

        return bbox.get_extent()
    
    # ---------------------------------------------------------

    @staticmethod
    def surface_area(mesh):
        """
        Calculates the total surface area of an Open3D mesh.

        Parameters
        ----------
        mesh : open3d.geometry.TriangleMesh
            Open3D mesh whose surface area will be calculated.

        Returns
        -------
        float
            Total surface area in squared model units.

            Examples:
                If the STL coordinates are in millimetres,
                the result will be in mm².

                If the STL coordinates are in metres,
                the result will be in m².
        """

        if mesh is None:
            raise ValueError(
                "The mesh cannot be None."
            )

        if mesh.is_empty():
            raise ValueError(
                "The surface area cannot be calculated "
                "because the mesh is empty."
            )

        if len(mesh.triangles) == 0:
            raise ValueError(
                "The surface area cannot be calculated "
                "because the mesh has no triangles."
            )

        trimesh_mesh = GeometryUtils.open3d_to_trimesh(
            mesh
        )

        area = float(
            trimesh_mesh.area
        )

        return area
    
    # ---------------------------------------------------------

    @staticmethod
    def volume(mesh):
        """
        Calculates the enclosed volume of an Open3D mesh.

        Parameters
        ----------
        mesh : open3d.geometry.TriangleMesh
            Open3D mesh whose enclosed volume will be calculated.

        Returns
        -------
        float
            Enclosed volume in cubic model units.

            Examples:
                If the STL coordinates are in millimetres,
                the result will be in mm³.

                If the STL coordinates are in metres,
                the result will be in m³.

        Raises
        ------
        ValueError
            If the mesh is empty, has no triangles or is not
            watertight.
        """

        if mesh is None:
            raise ValueError(
                "The mesh cannot be None."
            )

        if mesh.is_empty():
            raise ValueError(
                "The volume cannot be calculated "
                "because the mesh is empty."
            )

        if len(mesh.triangles) == 0:
            raise ValueError(
                "The volume cannot be calculated "
                "because the mesh has no triangles."
            )

        trimesh_mesh = GeometryUtils.open3d_to_trimesh(
            mesh
        )

        if not trimesh_mesh.is_watertight:
            raise ValueError(
                "The volume cannot be calculated reliably "
                "because the mesh is not watertight."
            )

        volume = float(
            abs(trimesh_mesh.volume)
        )

        return volume
    
    # ---------------------------------------------------------

    @staticmethod
    def center_of_mass(mesh):
        """
        Calculates the center of mass of an Open3D mesh.

        A homogeneous mass distribution is assumed.

        Parameters
        ----------
        mesh : open3d.geometry.TriangleMesh
            Closed Open3D mesh whose center of mass will
            be calculated.

        Returns
        -------
        numpy.ndarray
            Three-dimensional vector containing the center
            of mass coordinates:

                [x, y, z]

            The coordinates are expressed in the same length
            unit used by the STL model.

        Raises
        ------
        ValueError
            If the mesh is None, empty, has no triangles or
            is not watertight.
        """

        if mesh is None:
            raise ValueError(
                "The mesh cannot be None."
            )

        if mesh.is_empty():
            raise ValueError(
                "The center of mass cannot be calculated "
                "because the mesh is empty."
            )

        if len(mesh.triangles) == 0:
            raise ValueError(
                "The center of mass cannot be calculated "
                "because the mesh has no triangles."
            )

        trimesh_mesh = GeometryUtils.open3d_to_trimesh(
            mesh
        )

        if not trimesh_mesh.is_watertight:
            raise ValueError(
                "The center of mass cannot be calculated "
                "reliably because the mesh is not watertight."
            )

        center_mass = np.asarray(
            trimesh_mesh.center_mass,
            dtype=float
        )

        return center_mass.copy()
    
    # ---------------------------------------------------------

    @staticmethod
    def inertia_tensor(mesh, density=1.0):
        """
        Calculates the inertia tensor of an Open3D mesh.

        The tensor is calculated about the center of mass
        and expressed in the coordinate axes of the mesh.

        A homogeneous mass distribution is assumed.

        Parameters
        ----------
        mesh : open3d.geometry.TriangleMesh
            Closed Open3D mesh whose inertia tensor will
            be calculated.

        density : float, optional
            Homogeneous density expressed in mass units per
            cubic model unit.

            Examples:

                kg/mm³ for an STL expressed in millimetres.
                kg/cm³ for an STL expressed in centimetres.
                kg/m³  for an STL expressed in metres.

            The default value is 1.0.

        Returns
        -------
        numpy.ndarray
            Symmetric 3 x 3 inertia tensor:

                [[Ixx, Ixy, Ixz],
                 [Ixy, Iyy, Iyz],
                 [Ixz, Iyz, Izz]]

            The units are:

                mass unit × model length unit²

            For example:

                kg/mm³ and millimetres -> kg·mm²
                kg/m³ and metres       -> kg·m²

        Raises
        ------
        ValueError
            If the mesh is invalid, is not watertight, has
            zero volume or the supplied density is not a
            finite positive number.
        """

        if mesh is None:
            raise ValueError(
                "The mesh cannot be None."
            )

        if mesh.is_empty():
            raise ValueError(
                "The inertia tensor cannot be calculated "
                "because the mesh is empty."
            )

        if len(mesh.triangles) == 0:
            raise ValueError(
                "The inertia tensor cannot be calculated "
                "because the mesh has no triangles."
            )

        try:
            density = float(density)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "The density must be a valid number."
            ) from error

        if not np.isfinite(density):
            raise ValueError(
                "The density must be a finite number."
            )

        if density <= 0:
            raise ValueError(
                "The density must be greater than zero."
            )

        trimesh_mesh = GeometryUtils.open3d_to_trimesh(
            mesh
        )

        if not trimesh_mesh.is_watertight:
            raise ValueError(
                "The inertia tensor cannot be calculated "
                "reliably because the mesh is not watertight."
            )

        mesh_volume = abs(
            float(trimesh_mesh.volume)
        )

        if not np.isfinite(mesh_volume):
            raise ValueError(
                "The enclosed mesh volume is not finite."
            )

        if mesh_volume <= 0:
            raise ValueError(
                "The inertia tensor cannot be calculated "
                "because the enclosed volume is zero."
            )

        trimesh_mesh.density = density

        inertia = np.asarray(
            trimesh_mesh.moment_inertia,
            dtype=float
        )

        if inertia.shape != (3, 3):
            raise ValueError(
                "The calculated inertia tensor must have "
                "dimensions 3 x 3."
            )

        if not np.all(np.isfinite(inertia)):
            raise ValueError(
                "The calculated inertia tensor contains "
                "non-finite values."
            )

        return inertia.copy()