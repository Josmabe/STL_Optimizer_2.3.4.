"""
=========================================================
STL OPTIMIZER

Configuration File

Compatible with:
    Windows
    Linux
    SteamOS
    
Author:
    Jose María Beltrán Díaz
=========================================================
"""

from enum import Enum


# =========================================================
# LENGTH UNITS
# =========================================================

class LengthUnit(Enum):
    """
    Length units supported by the physical property
    calculations.
    """

    MILLIMETERS = "mm"
    CENTIMETERS = "cm"
    METERS = "m"


# =========================================================
# PHYSICAL PROPERTIES
# =========================================================

# STL files do not store an explicit length unit.
#
# This value must match the unit used when the model was
# exported from the CAD software.
STL_LENGTH_UNIT = LengthUnit.MILLIMETERS

# Real measured mass of the processed piece, expressed in kg.
#
# All STL files processed during the same execution will use
# this mass value.
#
# Files with different measured masses must be processed
# separately, changing this value before each execution.
PIECE_MASS_KG = 0.05


# =========================================================
# SIMPLIFICATION MODES
# =========================================================

class SimplificationMode(Enum):
    """
    Available mesh simplification methods.
    """

    TARGET_TRIANGLES = 1
    PERCENTAGE = 2


# =========================================================
# USER CONFIGURATION
# =========================================================

# ---------------------------------------------------------
# SIMPLIFICATION METHOD
# ---------------------------------------------------------

# TARGET_TRIANGLES
#     The optimized model will have approximately the
#     specified number of triangles.
#
# PERCENTAGE
#     The optimized model will keep the specified
#     percentage of the original triangles.

SIMPLIFICATION_MODE = (
    SimplificationMode.TARGET_TRIANGLES
)


# ---------------------------------------------------------
# Used only if TARGET_TRIANGLES mode is selected
# ---------------------------------------------------------

TARGET_TRIANGLES = 5000 #25000


# ---------------------------------------------------------
# Used only if PERCENTAGE mode is selected
# ---------------------------------------------------------

KEEP_PERCENTAGE = 0.35


# =========================================================
# QUALITY
# =========================================================

# Boundary preservation.
#
# Higher values preserve external edges better but reduce
# the simplification ratio.
#
# Recommended values:
#
# 1.0  -> Maximum simplification
# 2.0  -> Balanced
# 5.0  -> Preserve borders
# 10.0 -> Almost no border deformation
#
# Reserved for future Open3D versions.

BOUNDARY_WEIGHT = 2.0


# =========================================================
# CLEANUP
# =========================================================

REMOVE_DUPLICATED_VERTICES = True

REMOVE_DUPLICATED_TRIANGLES = True

REMOVE_DEGENERATED_TRIANGLES = True

REMOVE_NON_MANIFOLD_EDGES = True


# =========================================================
# SEARCH OPTIONS
# =========================================================

# If enabled, all subdirectories located inside INPUT_FOLDER
# will also be searched for STL files.

SEARCH_SUBDIRECTORIES = False


# =========================================================
# OUTPUT MODES
# =========================================================

class SaveMode(Enum):
    """
    Available optimized-file output modes.

    SAME_FOLDER
        Saves the optimized STL beside the original STL.

    OUTPUT_FOLDER
        Saves optimized STL files inside OUTPUT_FOLDER.

    RESULTS_FOLDER
        Saves optimized STL files and reports directly
        inside RESULTS_FOLDER.

    RESULTS_SUBFOLDER
        Creates a separate folder for each STL inside
        RESULTS_FOLDER and saves both the optimized STL and
        its report inside that folder.
    """

    SAME_FOLDER = 1
    OUTPUT_FOLDER = 2
    RESULTS_FOLDER = 3
    RESULTS_SUBFOLDER = 4


# ---------------------------------------------------------
# OUTPUT MODE
# ---------------------------------------------------------

# Available options:
#
# SaveMode.SAME_FOLDER
# SaveMode.OUTPUT_FOLDER
# SaveMode.RESULTS_FOLDER
# SaveMode.RESULTS_SUBFOLDER

SAVE_MODE = SaveMode.RESULTS_SUBFOLDER


# ---------------------------------------------------------
# OUTPUT OPTIONS
# ---------------------------------------------------------

# Used when SAVE_MODE is SaveMode.OUTPUT_FOLDER.

OUTPUT_FOLDER = "Optimized_STL"

# Suffix added to the optimized STL file name.

OUTPUT_SUFFIX = "_Optimized"

# Existing optimized files will only be overwritten if this
# option is enabled.

OVERWRITE_EXISTING = False

# Opens the output folder automatically after processing,
# if supported by the main program.

AUTO_OPEN_OUTPUT_FOLDER = False


# =========================================================
# DIRECTORIES
# =========================================================

# Folder containing the STL files to process.

INPUT_FOLDER = "Optimizable Mesh"

# Folder used for optimization reports and for the results
# modes.

RESULTS_FOLDER = "Results"


# =========================================================
# LOGGING
# =========================================================

PROGRAM_VERSION = "2.3.4"

SAVE_LOG_FILE = True

SHOW_PROGRESS = True

VERBOSE = True

SHOW_STATISTICS = True

SHOW_TIMES = True

LOG_SUFFIX = " Optimization Report"

# =========================================================
# PROCESS ISOLATION AND TIMEOUT
# =========================================================

# If enabled, every STL is processed inside an independent
# operating-system process. A blocked piece can therefore be
# terminated without stopping the complete batch.
ENABLE_PROCESS_TIMEOUT = True

# Maximum processing time allowed for each STL, in seconds.
# Example: 300 seconds = 5 minutes.
PROCESS_TIMEOUT_SECONDS = 300

# Time granted to a worker to close after terminate() before
# the parent escalates to kill().
TERMINATE_GRACE_SECONDS = 5

# =========================================================
# PHYSICAL PROPERTY FALLBACK
# =========================================================

# If the repaired mesh is not watertight, calculate its
# physical properties from a watertight convex hull instead.
# When the exact repaired mesh is watertight, a Convex Hull is
# also calculated as a supplementary simulation/reference set.
#
# The optimized STL itself is NOT replaced by the hull. The
# hull is used only as an approximation for volume, center of
# mass, density and inertia calculations.
ENABLE_CONVEX_HULL_FALLBACK = True

# =========================================================
# CONVEX HULL EXPORT AND VISUALIZATION
# =========================================================

# Save the Convex Hull generated for fallback calculations or
# as a supplementary simulation/reference model.
SAVE_CONVEX_HULL_STL = True

# Save a PNG image of the Convex Hull generated for fallback
# calculations or as a supplementary simulation/reference model.
SAVE_CONVEX_HULL_IMAGE = True

# Image resolution in pixels.
CONVEX_HULL_IMAGE_WIDTH = 1600
CONVEX_HULL_IMAGE_HEIGHT = 1200

# Camera elevation and azimuth used for the isometric view.
CONVEX_HULL_VIEW_ELEVATION = 25
CONVEX_HULL_VIEW_AZIMUTH = -55

# Display the calculated center of mass in the image.
SHOW_CENTER_OF_MASS_IN_HULL_IMAGE = True

# File-name suffixes for generated convex-hull artifacts.
CONVEX_HULL_STL_SUFFIX = "_Convex_Hull"
CONVEX_HULL_IMAGE_SUFFIX = "_Convex_Hull"
