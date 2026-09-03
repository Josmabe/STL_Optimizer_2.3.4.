@echo off
setlocal EnableExtensions
chcp 65001 > nul
pushd "%~dp0"

echo Creating a local Python environment...
where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python Launcher ^(py.exe^) was not found.
    echo Install 64-bit Python 3.12 and run this file again.
    popd
    pause
    exit /b 1
)

py -3.12 -m venv .venv
if errorlevel 1 goto :FAIL

".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :FAIL

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :FAIL

echo.
echo Installation completed successfully.
popd
pause
exit /b 0

:FAIL
echo.
echo ERROR: Installation failed.
popd
pause
exit /b 1
