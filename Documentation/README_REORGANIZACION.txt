STL OPTIMIZER v2.3.4 - REORGANIZED SOURCE PACKAGE
==================================================

STRUCTURE
---------
STL_Optimizer_2.3.4_SRC_CLEAN\
    STL_Optimizer_windows.bat
    INSTALL_DEPENDENCIES.bat
    requirements.txt
    src\
        STL_Optimizer.py
        config_API.py
        ...
    Documentation\
        README files
        User manuals
        Technical manuals
    Optimizable Mesh\
    Results\

IMPORTANT
---------
This package intentionally does not include the old .venv folder.
Virtual environments contain thousands of files and absolute references,
and were the cause of the Windows extraction errors in the previous ZIPs.

The Python source files are now stored inside the src folder. The Windows
launcher keeps the project root as the working directory, so the relative
folders "Optimizable Mesh", "Results" and "Documentation" continue to work.

TO USE YOUR ALREADY WORKING ENVIRONMENT
---------------------------------------
1. Extract this package.
2. Copy the complete .venv folder from the original working project into
   this folder, beside STL_Optimizer_windows.bat.
3. Run STL_Optimizer_windows.bat.

TO CREATE A CLEAN ENVIRONMENT
-----------------------------
1. Install 64-bit Python 3.12.
2. Run INSTALL_DEPENDENCIES.bat once.
3. Run STL_Optimizer_windows.bat.

NOTES
-----
- Keep the .venv folder in the project root, not inside src.
- Do not copy __pycache__ folders; Python recreates them automatically.
- Keep requirements.txt in the project root.
- Store project manuals and README files inside Documentation.
- On Windows, Open3D may fail when the complete project path contains
  accented or non-ASCII characters. Use a path containing only standard
  English characters, for example:

      C:\STL_Optimizer_2.3.4\

VERSION
-------
v2.3.4
- Added supplementary Convex Hull physical properties for watertight repaired meshes.
- Convex Hull STL and PNG are also generated after exact calculations.
- Reports distinguish exact repaired-mesh data from Convex Hull data.

v2.3.3
- Python source files moved into the src folder.
- Documentation folder added for manuals and README files.
- Windows launcher adapted to the reorganized structure.
- Dependency installation retained through requirements.txt and
  INSTALL_DEPENDENCIES.bat.
- No intentional functional changes compared with v2.3.2.