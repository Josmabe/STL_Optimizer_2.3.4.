"""
=========================================================
STL OPTIMIZER

Mass Processor

Calculates physical properties from a watertight triangular
mesh using a real measured mass.

The calculated center of mass is expressed in metres and the
inertia tensor is expressed in kg·m².

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

import numpy as np

from config_API import PIECE_MASS_KG, STL_LENGTH_UNIT, LengthUnit
from geometry_utils import GeometryUtils


class MassProcessor:
    """Calculates physical properties of a watertight mesh."""

    def __init__(self, mesh):
        self.mesh = mesh
        try:
            self.mass_kg = float(PIECE_MASS_KG)
        except (TypeError, ValueError) as error:
            raise ValueError("PIECE_MASS_KG must be a valid number.") from error

        self.length_unit = STL_LENGTH_UNIT
        self._reset_results()

    def _reset_results(self):
        self.length_scale_to_meters = 1.0
        self.volume_model_units = 0.0
        self.volume_m3 = 0.0
        self.density_kg_model_unit3 = 0.0
        self.density_kg_m3 = 0.0
        self.center_of_mass_model_units = None
        self.center_of_mass_m = None
        self.inertia_tensor_model_units = None
        self.inertia_tensor_kg_m2 = None
        self.calculation_completed = False

    def _validate_inputs(self):
        if self.mesh is None:
            raise ValueError("The mesh cannot be None.")
        if self.mesh.is_empty():
            raise ValueError(
                "Physical properties cannot be calculated because the mesh is empty."
            )
        if len(self.mesh.triangles) == 0:
            raise ValueError(
                "Physical properties cannot be calculated because the mesh has no triangles."
            )
        if not np.isfinite(self.mass_kg):
            raise ValueError("PIECE_MASS_KG must be a finite number.")
        if self.mass_kg <= 0:
            raise ValueError("PIECE_MASS_KG must be greater than zero.")

    def _get_length_scale_to_meters(self):
        conversion_factors = {
            LengthUnit.MILLIMETERS: 1e-3,
            LengthUnit.CENTIMETERS: 1e-2,
            LengthUnit.METERS: 1.0,
        }
        if self.length_unit not in conversion_factors:
            raise ValueError("Unsupported STL length unit.")
        return conversion_factors[self.length_unit]

    def calculate(self):
        """
        Calculates all physical properties from one shared Trimesh object.

        This preserves the exact v2.3 geometry and formulas while avoiding
        repeated Open3D-to-Trimesh conversions and repeated watertight checks.
        """
        self._reset_results()
        self._validate_inputs()

        trimesh_mesh = GeometryUtils.open3d_to_trimesh(self.mesh)
        if not trimesh_mesh.is_watertight:
            raise ValueError(
                "Physical properties cannot be calculated reliably because "
                "the mesh is not watertight."
            )

        self.length_scale_to_meters = self._get_length_scale_to_meters()

        self.volume_model_units = abs(float(trimesh_mesh.volume))
        if not np.isfinite(self.volume_model_units):
            raise ValueError("The enclosed mesh volume is not finite.")
        if self.volume_model_units <= 0:
            raise ValueError("The enclosed mesh volume must be greater than zero.")

        self.volume_m3 = self.volume_model_units * (
            self.length_scale_to_meters ** 3
        )
        if not np.isfinite(self.volume_m3):
            raise ValueError("The converted mesh volume is not finite.")
        if self.volume_m3 <= 0:
            raise ValueError("The converted mesh volume must be greater than zero.")

        self.density_kg_model_unit3 = self.mass_kg / self.volume_model_units
        self.density_kg_m3 = self.mass_kg / self.volume_m3

        self.center_of_mass_model_units = np.asarray(
            trimesh_mesh.center_mass, dtype=float
        ).copy()
        if self.center_of_mass_model_units.shape != (3,):
            raise ValueError(
                "The calculated center of mass must contain exactly three coordinates."
            )
        if not np.all(np.isfinite(self.center_of_mass_model_units)):
            raise ValueError(
                "The calculated center of mass contains non-finite values."
            )
        self.center_of_mass_m = (
            self.center_of_mass_model_units * self.length_scale_to_meters
        )

        trimesh_mesh.density = self.density_kg_model_unit3
        self.inertia_tensor_model_units = np.asarray(
            trimesh_mesh.moment_inertia, dtype=float
        ).copy()
        if self.inertia_tensor_model_units.shape != (3, 3):
            raise ValueError(
                "The calculated inertia tensor must have dimensions 3 x 3."
            )
        if not np.all(np.isfinite(self.inertia_tensor_model_units)):
            raise ValueError(
                "The calculated inertia tensor contains non-finite values."
            )

        self.inertia_tensor_kg_m2 = self.inertia_tensor_model_units * (
            self.length_scale_to_meters ** 2
        )
        self.calculation_completed = True
        return self.statistics()

    def statistics(self):
        return {
            "mass_kg": self.mass_kg,
            "length_unit": self.length_unit.value,
            "length_scale_to_meters": self.length_scale_to_meters,
            "volume_model_units": self.volume_model_units,
            "volume_m3": self.volume_m3,
            "density_kg_model_unit3": self.density_kg_model_unit3,
            "density_kg_m3": self.density_kg_m3,
            "center_of_mass_model_units": self._copy_array(
                self.center_of_mass_model_units
            ),
            "center_of_mass_m": self._copy_array(self.center_of_mass_m),
            "inertia_tensor_model_units": self._copy_array(
                self.inertia_tensor_model_units
            ),
            "inertia_tensor_kg_m2": self._copy_array(
                self.inertia_tensor_kg_m2
            ),
            "calculation_completed": self.calculation_completed,
        }

    @staticmethod
    def _copy_array(array):
        if array is None:
            return None
        return np.asarray(array, dtype=float).copy()
