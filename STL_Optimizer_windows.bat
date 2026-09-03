@echo off
setlocal EnableExtensions
chcp 65001 > nul
title STL OPTIMIZER v2.3.4

REM Work from the folder containing this launcher.
pushd "%~dp0"

set "ROOT_DIR=%CD%"
set "SRC_DIR=%ROOT_DIR%\src"
set "PYTHON_EXE=%ROOT_DIR%\.venv\Scripts\python.exe"

cls
echo ===============================================================
echo.
echo                      STL OPTIMIZER v2.3.4
echo.
echo          Automatic STL Mesh Optimization Tool
echo.
echo          Tesis Fin de Master
echo          Jose Maria Beltran Diaz
echo.
echo ===============================================================
echo.
echo Compatible with:
echo     - Windows
echo     - Linux
echo     - SteamOS
echo.
echo ===============================================================
echo.
echo Starting application...
echo.

if not exist "%SRC_DIR%\STL_Optimizer.py" (
    echo ERROR: Missing file:
    echo   "%SRC_DIR%\STL_Optimizer.py"
    echo.
    set "EXIT_CODE=3"
    goto :END
)

if not exist "%PYTHON_EXE%" (
    echo ERROR: The virtual environment was not found:
    echo   "%PYTHON_EXE%"
    echo.
    echo Copy the .venv folder from your working original project
    echo beside this BAT file, or run INSTALL_DEPENDENCIES.bat.
    echo.
    set "EXIT_CODE=2"
    goto :END
)

set "PYTHONPATH=%SRC_DIR%;%PYTHONPATH%"
"%PYTHON_EXE%" -u "%SRC_DIR%\STL_Optimizer.py"
set "EXIT_CODE=%ERRORLEVEL%"

:END
echo.

echo.
echo ===============================================================
echo.
echo                 STL OPTIMIZER HAS FINISHED
echo.
echo ===============================================================
echo.

if "%EXIT_CODE%"=="0" (
    echo Status: SUCCESS
) else (
    echo Status: ERROR ^(code %EXIT_CODE%^)
)


echo.
echo If not fatal error occurr all available information will be saved in:
echo.	
echo	Results/
echo    	Mesh/
echo.
echo                 Thank you for using STL OPTIMIZER v2.3.4.
echo.

echo ===============================================================
echo.

popd
pause
endlocal & exit /b %EXIT_CODE%
