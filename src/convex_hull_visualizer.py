"""
=========================================================
STL OPTIMIZER

Convex Hull Visualizer

Creates a headless PNG visualization of the exact convex-hull
mesh used for approximate physical-property calculations.

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from config_API import (
    CONVEX_HULL_IMAGE_HEIGHT,
    CONVEX_HULL_IMAGE_WIDTH,
    CONVEX_HULL_VIEW_AZIMUTH,
    CONVEX_HULL_VIEW_ELEVATION,
    SHOW_CENTER_OF_MASS_IN_HULL_IMAGE,
)


class ConvexHullVisualizer:
    """Generates a PNG from an Open3D convex-hull mesh."""

    @staticmethod
    def _validate_mesh(mesh):
        if mesh is None:
            raise ValueError("The convex-hull mesh cannot be None.")
        if mesh.is_empty():
            raise ValueError("The convex-hull mesh is empty.")
        if len(mesh.vertices) == 0 or len(mesh.triangles) == 0:
            raise ValueError("The convex-hull mesh has no geometry.")

    @staticmethod
    def _equal_axes(ax, vertices):
        minimum = vertices.min(axis=0)
        maximum = vertices.max(axis=0)
        center = (minimum + maximum) / 2.0
        radius = max(float(np.max(maximum - minimum)) / 2.0, 1e-12)
        ax.set_xlim(center[0] - radius, center[0] + radius)
        ax.set_ylim(center[1] - radius, center[1] + radius)
        ax.set_zlim(center[2] - radius, center[2] + radius)
        ax.set_box_aspect((1, 1, 1))

    @classmethod
    def save(cls, mesh, output_path, center_of_mass=None, title=None):
        """Saves the exact calculation hull as a PNG image."""
        cls._validate_mesh(mesh)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        vertices = np.asarray(mesh.vertices, dtype=float)
        triangles = np.asarray(mesh.triangles, dtype=int)
        faces = vertices[triangles]

        dpi = 100
        width = max(int(CONVEX_HULL_IMAGE_WIDTH), 400)
        height = max(int(CONVEX_HULL_IMAGE_HEIGHT), 300)
        figure = None

        try:
            figure = plt.figure(
                figsize=(width / dpi, height / dpi),
                dpi=dpi,
            )
            ax = figure.add_subplot(111, projection="3d")

            collection = Poly3DCollection(
                faces,
                linewidths=0.25,
                edgecolors="black",
                alpha=0.88,
            )
            collection.set_facecolor((0.45, 0.60, 0.85, 1.0))
            ax.add_collection3d(collection)

            cls._equal_axes(ax, vertices)
            ax.view_init(
                elev=float(CONVEX_HULL_VIEW_ELEVATION),
                azim=float(CONVEX_HULL_VIEW_AZIMUTH),
            )
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
            ax.set_title(title or "Convex Hull used for inertia calculation")

            if SHOW_CENTER_OF_MASS_IN_HULL_IMAGE and center_of_mass is not None:
                center = np.asarray(center_of_mass, dtype=float).reshape(3)
                if np.all(np.isfinite(center)):
                    ax.scatter(
                        center[0], center[1], center[2],
                        s=70, marker="o", depthshade=False,
                        label="Center of mass",
                    )
                    ax.legend(loc="upper right")

            ax.text2D(
                0.02,
                0.02,
                "This is the exact convex-hull mesh used for the "
                "approximate physical properties.",
                transform=ax.transAxes,
            )
            figure.tight_layout()
            figure.savefig(output_path, dpi=dpi, bbox_inches="tight")
        finally:
            if figure is not None:
                plt.close(figure)

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("The convex-hull image could not be saved.")

        return output_path
