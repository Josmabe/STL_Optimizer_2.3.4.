STL OPTIMIZER v2.3.4
======================

Author
------
José María Beltrán Díaz

Description
-----------
STL Optimizer is a utility for batch-processing STL files. It repairs common mesh
defects, attempts to obtain a watertight mesh, simplifies the geometry, exports
an optimized STL and, whenever possible, calculates the physical properties of
the part (volume, centre of mass and inertia tensor).

Physical properties are calculated from the exact repaired mesh whenever it is
watertight. In that case, version 2.3.4 also calculates a separate Convex Hull
property set for simulation/reference, and exports the corresponding Convex
Hull STL and PNG when enabled. If the repaired mesh is not watertight, the same
Convex Hull remains available as the fallback physical-property calculation.
The optimized STL always corresponds to the simplified repaired mesh, never to
the Convex Hull.

Version 2.3.3 reorganised the project structure by placing all Python source
files inside the "src" directory. Version 2.3.4 keeps that structure and adds
the supplementary Convex Hull physical-property dataset and simulation/reference
artifacts described below.

Main features
-------------
- Batch processing of STL files.
- Recursive search (configurable).
- Automatic mesh repair:
    * Duplicated vertices.
    * Duplicated triangles.
    * Degenerate triangles.
    * Non-manifold edges.
    * Unreferenced vertices.
    * Normal recomputation.
- Watertight repair stage.
- Mesh simplification.
- Exact physical-property calculation whenever possible.
- Supplementary Convex Hull physical properties when exact calculation succeeds.
- Automatic Convex Hull fallback approximation when exact calculation is impossible.
- Optional export of:
    * Convex Hull STL.
    * Convex Hull image (PNG).
- Individual processing report for every STL.
- Global execution summary.
- Per-file and total execution times.
- Independent worker process per STL with configurable timeout.

Folder structure
----------------

STL_Optimizer/
│
├── .venv/                    # Generated locally; not included in repository
│   Python virtual environment.
│
├── src/
│   Python source code.
│
├── Documentation/
│   Project documentation:
│       - User manuals.
│       - Technical manuals.
│       - README files.
│       - Release notes.
│
├── Optimizable Mesh/
│   Place the STL files to process here.
│
├── Results/
│   Automatically created output folder containing:
│       - Optimized STL files.
│       - Report (.txt) for every processed STL.
│       - Optional Convex Hull STL.
│       - Optional Convex Hull PNG.
│
├── STL_Optimizer_windows.bat
│   Windows launcher.
│
├── INSTALL_DEPENDENCIES.bat
│   Creates the virtual environment and installs all dependencies.
│
└── requirements.txt
    Python package list.

Configuration
-------------
Most settings are located in:

    src/config_API.py

Among others:
- Input/output folders.
- Simplification percentage.
- Target triangle count.
- Piece mass.
- STL length units.
- Timeout.
- Convex Hull behaviour.
- Logging options.
- Overwrite behaviour.

Execution
---------

Windows

    Double-click:

        STL_Optimizer_windows.bat

The launcher automatically activates the virtual environment and executes:

    src/STL_Optimizer.py

Requirements
------------

Python 3.12 (recommended)

Install dependencies using:

    INSTALL_DEPENDENCIES.bat

or

    pip install -r requirements.txt

Main libraries:
- Open3D
- Trimesh
- NumPy
- SciPy
- NetworkX
- Matplotlib (only required when Convex Hull images are generated)

Processing pipeline
-------------------

1. Locate STL files.
2. Load mesh.
3. Repair mesh.
4. Attempt watertight repair.
5. Preserve repaired mesh for physical calculations.
6. Simplify mesh.
7. Calculate the primary physical properties:
       - Exact repaired mesh whenever watertight, or
       - Convex Hull fallback if exact calculation is impossible.
8. When exact calculation succeeds, also calculate supplementary Convex Hull
   physical properties for simulation/reference.
9. Save optimized STL.
10. Export optional Convex Hull STL and PNG artifacts.
11. Generate processing report with clearly separated exact and hull data.

Result interpretation
---------------------

SUCCESS
    STL optimized and physical properties calculated successfully.

PARTIAL SUCCESS
    STL optimized successfully, but physical properties required a Convex Hull
    approximation or could not be calculated.

FAILED
    The STL could not be processed successfully.

Notes
-----

- Physical properties are always calculated from the repaired full-resolution
  mesh whenever it is watertight.
- Simplification never affects the accuracy of the physical calculations.
- Convex Hull is used as a supplementary simulation/reference calculation when
  exact repaired-mesh properties are available, and as fallback otherwise.
- Each STL is processed in an isolated operating-system process. A failure or
  timeout in one file does not stop the rest of the batch.
- The Python virtual environment (.venv) is created locally by 
  INSTALL_DEPENDENCIES.bat and is not distributed with the repository.
- The "__pycache__" folders are automatically generated and should not be
  distributed.
- On Windows, Open3D cannot load STL files whose path contains accented or
  non-ASCII characters (for example: á, é, í, ó, ú or ñ). If this occurs,
  move the project to a folder whose complete path only contains standard
  English characters.

Version history
---------------

v2.3.4
- Added supplementary Convex Hull physical-property calculations when the exact
  repaired mesh is watertight.
- Convex Hull STL and PNG are now generated for exact-calculation cases too.
- Reports now separate exact repaired-mesh properties from Convex Hull values.
- Convex Hull remains the fallback method when exact calculation is impossible.

v2.3.3
- Project reorganised using a dedicated "src" directory.
- Windows launcher updated to support the new structure.
- Installation simplified using requirements.txt.
- Added INSTALL_DEPENDENCIES.bat.
- Added documentation for the Python virtual environment.
- Added documentation for Open3D path limitations on Windows.
- Improved project organisation and portability.
- No intentional functional changes compared with v2.3.2.

v2.3.2
- Internal performance optimisations.
- Execution-time measurements.
- Improved logging.
- Improved robustness.
- No intentional functional changes compared with v2.3.
