@echo off
REM Post-build script for Windows to separate PySide6 for GPL compliance
REM This script reorganizes the PyInstaller output to separate PySide6 libraries
REM Strategy: Keep Python packages in _internal but move DLLs to pyside6/lib

setlocal enabledelayedexpansion

set DIST_DIR=dist-windows\fdr
set PYSIDE_DIR=%DIST_DIR%\pyside6

REM Create pyside6 directory structure
mkdir "%PYSIDE_DIR%"
mkdir "%PYSIDE_DIR%\lib"
mkdir "%PYSIDE_DIR%\Qt\lib"
mkdir "%PYSIDE_DIR%\plugins"

echo Separating PySide6 libraries...

REM Move Qt6 DLLs from _internal root to pyside6\lib
for /r "%DIST_DIR%\_internal" %%f in (*Qt6*.dll) do (
    echo   Moving %%~nxf to pyside6\lib...
    move "%%f" "%PYSIDE_DIR%\lib\" >nul
)

REM Move shiboken6 DLLs
for /r "%DIST_DIR%\_internal" %%f in (*shiboken*.dll) do (
    echo   Moving %%~nxf to pyside6\lib...
    move "%%f" "%PYSIDE_DIR%\lib\" >nul
)

REM Copy Qt6 libraries from PySide6\Qt\lib to pyside6\Qt\lib
if exist "%DIST_DIR%\_internal\PySide6\Qt\lib\" (
    echo   Copying Qt libraries to pyside6\Qt\lib...
    xcopy "%DIST_DIR%\_internal\PySide6\Qt\lib\*.*" "%PYSIDE_DIR%\Qt\lib\" /E /Y /Q >nul
)

REM Copy Qt plugins
if exist "%DIST_DIR%\_internal\PySide6\Qt\plugins\" (
    echo   Copying Qt plugins to pyside6\plugins...
    xcopy "%DIST_DIR%\_internal\PySide6\Qt\plugins\*" "%PYSIDE_DIR%\plugins\" /E /Y /Q >nul
)

REM Create junctions (symlinks) for PySide6 and shiboken6 in pyside6 for clarity
if exist "%DIST_DIR%\_internal\PySide6" (
    echo   Creating junction to PySide6 in pyside6...
    mklink /J "%PYSIDE_DIR%\PySide6" "%DIST_DIR%\_internal\PySide6" >nul 2>&1
    if errorlevel 1 (
        echo   (Junction failed, copying instead...)
        xcopy "%DIST_DIR%\_internal\PySide6" "%PYSIDE_DIR%\PySide6\" /E /Y /Q >nul
    )
)

if exist "%DIST_DIR%\_internal\shiboken6" (
    echo   Creating junction to shiboken6 in pyside6...
    mklink /J "%PYSIDE_DIR%\shiboken6" "%DIST_DIR%\_internal\shiboken6" >nul 2>&1
    if errorlevel 1 (
        echo   (Junction failed, copying instead...)
        xcopy "%DIST_DIR%\_internal\shiboken6" "%PYSIDE_DIR%\shiboken6\" /E /Y /Q >nul
    )
)

REM Backup original executable
if exist "%DIST_DIR%\fdr.exe" (
    echo   Backing up original executable...
    move "%DIST_DIR%\fdr.exe" "%DIST_DIR%\fdr_bin.exe" >nul
)

REM Create launcher batch file
(
    echo @echo off
    echo REM Flight Data Recorder Launcher
    echo REM Configures environment for PySide6 GPL compliance
    echo.
    echo set SCRIPT_DIR=%%~dp0
    echo set PYSIDE_DIR=%%SCRIPT_DIR%%pyside6
    echo.
    echo REM Add PySide6 libraries to PATH
    echo set PATH=%%PYSIDE_DIR%%\lib;%%PYSIDE_DIR%%\Qt\lib;%%PATH%%
    echo.
    echo REM Add PySide6 to Qt plugin path
    echo set QT_PLUGIN_PATH=%%PYSIDE_DIR%%\plugins;%%QT_PLUGIN_PATH%%
    echo.
    echo REM Execute the actual binary
    echo start /b "" "%%SCRIPT_DIR%%fdr_bin.exe" %%*
) > "%DIST_DIR%\fdr.bat"

echo.
echo Post-build processing complete!
echo ================================
echo Structure:
echo   %DIST_DIR%\
echo     +--- fdr.bat       (launcher script)
echo     +--- fdr_bin.exe   (actual executable)
echo     +--- _internal\   (other dependencies)
echo     \--- pyside6\     (PySide6 libraries - GPL compliant)
echo.
echo To run: %DIST_DIR%\fdr.bat
echo.
pause
