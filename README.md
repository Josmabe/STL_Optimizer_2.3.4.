# STL Optimizer

**STL Optimizer v2.3.4** is a Python-based utility designed for the automatic batch processing, repair, simplification and analysis of STL meshes.

The tool was developed as part of the **Modeling and Simulation of a Hexapod Robot** project, with the aim of preparing complex STL geometries for their use in simulation environments while preserving the original geometry whenever possible.

STL Optimizer can automatically repair common mesh defects, attempt to obtain a watertight representation, simplify the geometry and calculate physical properties such as **volume, centre of mass and inertia tensor**.

When the repaired mesh is watertight, physical properties are calculated directly from the full-resolution repaired geometry. A separate **Convex Hull** representation can also be generated as a supplementary dataset for simulation and comparison. If an exact calculation is not possible, the Convex Hull is used as a fallback approximation.

> **Important:** The optimized STL always corresponds to the simplified repaired mesh. The Convex Hull is never used as a replacement for the optimized STL.

---

## Main Features

- Automatic batch processing of STL files.
- Configurable recursive file search.
- Mesh repair:
  - Duplicated vertices.
  - Duplicated triangles.
  - Degenerate triangles.
  - Non-manifold edges.
  - Unreferenced vertices.
  - Normal recomputation.
- Watertight mesh repair stage.
- Mesh simplification.
- Physical-property calculation from the full-resolution repaired mesh whenever possible.
- Calculation of:
  - Volume.
  - Centre of mass.
  - Inertia tensor.
- Supplementary Convex Hull physical-property calculation.
- Automatic Convex Hull fallback when exact calculation is not possible.
- Optional Convex Hull STL export.
- Optional Convex Hull PNG visualization.
- Individual processing report for each STL.
- Global execution summary.
- Per-file and total execution-time measurement.
- Independent worker process for each STL with configurable timeout.

---

## Processing Pipeline

The general STL Optimizer workflow is:

1. Locate STL files.
2. Load the mesh.
3. Repair common mesh defects.
4. Attempt watertight repair.
5. Preserve the full-resolution repaired mesh for physical calculations.
6. Simplify the repaired mesh.
7. Calculate the primary physical properties:
   - From the exact repaired mesh when watertight.
   - From the Convex Hull as a fallback when exact calculation is not possible.
8. Calculate supplementary Convex Hull properties when exact calculation succeeds.
9. Save the optimized STL.
10. Export optional Convex Hull STL and PNG files.
11. Generate the individual processing report.
12. Generate the global execution summary.

---

## Workflow Diagram

![STL Optimizer workflow](Documentation/Diagrama%20de%20Flujo%20de%20STL%20Optimizer%202.3.4_Clean.png)

---

## Project Structure

```text
STL_Optimizer/
│
├── src/
│   ├── STL_Optimizer.py
│   ├── config_API.py
│   ├── convex_hull_visualizer.py
│   ├── file_manager.py
│   ├── geometry_utils.py
│   ├── logger.py
│   ├── mass_processor.py
│   ├── mesh_processor.py
│   ├── repair_processor.py
│   ├── time_utils.py
│   └── watertight_processor.py
│
├── Documentation/
│   ├── STL_Optimizer_v2.3.4_Complete_Manual_EN.docx
│   ├── STL_Optimizer_v2.3.4_Complete_Manual_ES.docx
│   ├── README.txt
│   └── ...
│
├── Optimizable Mesh/
│   └── .gitkeep
│
├── Results/
│   └── .gitkeep
│
├── INSTALL_DEPENDENCIES.bat
├── STL_Optimizer_windows.bat
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

The `.venv` virtual environment is created locally during installation and is therefore not included in the repository.

---

## Requirements

- **Python 3.12** recommended.
- Windows for the included `.bat` installation and launcher scripts.

Main Python dependencies:

- Open3D
- Trimesh
- NumPy
- SciPy
- NetworkX
- Matplotlib

The exact Python package requirements are defined in:

```text
requirements.txt
```

---

## Installation

### Windows

Clone or download the repository and place it in a local directory.

Then run:

```text
INSTALL_DEPENDENCIES.bat
```

The installation script creates the local Python virtual environment and installs the required dependencies from `requirements.txt`.

The generated `.venv` directory must remain in the project root for the Windows launcher to work correctly.

### Manual installation

Dependencies can also be installed manually using:

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Add the STL files

Place the STL files to be processed inside:

```text
Optimizable Mesh/
```

Recursive folder processing can be enabled or disabled in the configuration.

### 2. Configure STL Optimizer

The main configuration parameters are located in:

```text
src/config_API.py
```

Available settings include:

- Input and output directories.
- Simplification percentage.
- Target triangle count.
- Real piece mass.
- STL length units.
- Processing timeout.
- Convex Hull behaviour.
- Logging options.
- Overwrite behaviour.

### 3. Run STL Optimizer

On Windows, double-click:

```text
STL_Optimizer_windows.bat
```

The launcher activates the local virtual environment and executes:

```text
src/STL_Optimizer.py
```

### 4. Check the results

Generated files are stored inside:

```text
Results/
```

Depending on the configuration and processing result, this directory can contain:

- Optimized STL.
- Individual TXT processing report.
- Convex Hull STL.
- Convex Hull PNG.

---

## Physical Properties

STL Optimizer distinguishes between two physical-property calculation methods.

### Exact repaired mesh

Whenever the repaired full-resolution mesh is watertight, it is used as the primary source for calculating physical properties.

This calculation is performed **before mesh simplification**, so simplification does not affect the physical-property dataset.

### Convex Hull

The Convex Hull has two possible roles:

- **Supplementary calculation:** when the repaired mesh is watertight, a separate Convex Hull dataset can be generated for simulation and comparison.
- **Fallback calculation:** when physical properties cannot be obtained from the repaired mesh, the Convex Hull can provide an approximate alternative.

The Convex Hull does **not** replace the optimized STL geometry.

---

## Processing Results

Each STL can produce one of the following general outcomes:

**SUCCESS**

The STL was optimized and its physical properties were successfully calculated.

**PARTIAL SUCCESS**

The STL was optimized, but the physical-property calculation required the Convex Hull approximation or could not be completed exactly.

**FAILED**

The STL could not be processed successfully.

A failure or timeout affecting one STL does not stop the remaining batch, since every STL is processed in an isolated operating-system process.

---

## Documentation

Additional documentation is available in the [`Documentation`](Documentation/) directory.

It includes:

- Complete user and technical manual — English.
- Complete user and technical manual — Spanish.
- Detailed README.
- STL Optimizer workflow diagram.

---

## Windows Path Limitation

On Windows, Open3D may be unable to load STL files when their complete path contains accented or non-ASCII characters, such as:

```text
á é í ó ú ñ
```

If this occurs, move the repository to a directory whose complete path contains only standard ASCII characters.

For example:

```text
C:\STL_Optimizer\
```

---

## Version

Current release:

**STL Optimizer v2.3.4**

Main changes introduced in v2.3.4:

- Supplementary Convex Hull physical-property calculations.
- Convex Hull STL and PNG generation for exact-calculation cases.
- Separation of exact repaired-mesh and Convex Hull data in processing reports.
- Convex Hull fallback maintained when exact calculation is not possible.

See the documentation for additional version history.

---

## Author

**José María Beltrán Díaz**

Developed as part of the Master's Thesis:

**Modeling and Simulation of a Hexapod Robot**

---

## License

This project is distributed under the **GNU General Public License v3.0**.

See the [`LICENSE`](LICENSE) file for the complete license text.
