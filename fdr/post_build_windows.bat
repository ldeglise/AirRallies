@echo off
REM Post-build script for Windows to separate PySide6 for GPL compliance
REM Adapted for GitHub Actions (no mklink, no pause)

setlocal enabledelayedexpansion

set DIST_DIR=dist-windows\fdr
set PYSIDE_DIR=%DIST_DIR%\pyside6

REM Create pyside6 directory structure
mkdir "%PYSIDE_DIR%"
mkdir "%PYSIDE_DIR%\lib"
mkdir "%PYSIDE_DIR%\Qt\lib"
mkdir "%PYSIDE_DIR%\plugins"

echo Separating PySide6 libraries...

REM First, copy PySide6 and shiboken6 directories to pyside6
if exist "%DIST_DIR%\_internal\PySide6" (
    echo   Copying PySide6 to pyside6...
    xcopy "%DIST_DIR%\_internal\PySide6" "%PYSIDE_DIR%\PySide6" /E /Y /Q >nul
)

if exist "%DIST_DIR%\_internal\shiboken6" (
    echo   Copying shiboken6 to pyside6...
    xcopy "%DIST_DIR%\_internal\shiboken6" "%PYSIDE_DIR%\shiboken6" /E /Y /Q >nul
)

REM Copy all Qt6 DLLs from _internal to pyside6\lib (use copy, not move!)
for /r "%DIST_DIR%\_internal" %%f in (*Qt6*.dll) do (
    echo   Copying %%~nxf to pyside6\lib...
    copy "%%f" "%PYSIDE_DIR%\lib" >nul
)

REM Copy all shiboken6 DLLs from _internal to pyside6\lib (use copy, not move!)
for /r "%DIST_DIR%\_internal" %%f in (*shiboken*.dll) do (
    echo   Copying %%~nxf to pyside6\lib...
    copy "%%f" "%PYSIDE_DIR%\lib" >nul
)

REM Copy any PySide6 DLLs from _internal\PySide6 directory
if exist "%DIST_DIR%\_internal\PySide6\*.dll" (
    echo   Copying PySide6 DLLs to pyside6\lib...
    copy "%DIST_DIR%\_internal\PySide6\*.dll" "%PYSIDE_DIR%\lib" >nul
)

REM Copy any shiboken6 DLLs from _internal\shiboken6 directory
if exist "%DIST_DIR%\_internal\shiboken6\*.dll" (
    echo   Copying shiboken6 DLLs to pyside6\lib...
    copy "%DIST_DIR%\_internal\shiboken6\*.dll" "%PYSIDE_DIR%\lib" >nul
)

REM Copy Qt6 libraries from PySide6\Qt\lib to pyside6\Qt\lib
if exist "%DIST_DIR%\_internal\PySide6\Qt\lib" (
    echo   Copying Qt libraries to pyside6\Qt\lib...
    xcopy "%DIST_DIR%\_internal\PySide6\Qt\lib\*.*" "%PYSIDE_DIR%\Qt\lib" /E /Y /Q >nul
)

REM Copy Qt plugins
if exist "%DIST_DIR%\_internal\PySide6\Qt\plugins" (
    echo   Copying Qt plugins to pyside6\plugins...
    xcopy "%DIST_DIR%\_internal\PySide6\Qt\plugins\*" "%PYSIDE_DIR%\plugins" /E /Y /Q >nul
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
    echo REM Add PySide6 to Python path
    echo set PYTHONPATH=%%PYSIDE_DIR%%\PySide6;%%PYSIDE_DIR%%\shiboken6;%%PYTHONPATH%%
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