@echo off
REM Steven build script - call from VS2005 Command Prompt or with vcvarsall.bat sourced
REM Usage: build.cmd [debug|release]
REM
REM Requires:
REM   - Visual C++ 2005 (cl.exe + link.exe in PATH)
REM   - GAMEBRYO_SDK environment variable set to the eval SDK DEST_APP_PATH directory
REM     Example: set GAMEBRYO_SDK=C:\smtimagine\Gamebryo_2.3_eval\SDK\DEST_APP_PATH

if "%GAMEBRYO_SDK%"=="" (
    echo ERROR: GAMEBRYO_SDK environment variable not set.
    echo Set it to the Gamebryo eval SDK DEST_APP_PATH directory.
    exit /b 1
)

set CONFIG=%1
if "%CONFIG%"=="" set CONFIG=release

set SRCDIR=%~dp0src
set OUTDIR=%~dp0build\out\%CONFIG%
set INCDIR=%GAMEBRYO_SDK%\Win32\Include

if /i "%CONFIG%"=="debug" (
    set LIBDIR=%GAMEBRYO_SDK%\Win32\Lib\VC80\DebugLib
    set CFLAGS=/Od /MDd /DNIDEBUG /D_DEBUG /DWIN32 /D_WINDOWS /DSTRICT /Zi
    set LFLAGS=/DEBUG
) else (
    set LIBDIR=%GAMEBRYO_SDK%\Win32\Lib\VC80\ReleaseLib
    set CFLAGS=/O2 /MD /DNIRELEASE /DNDEBUG /DWIN32 /D_WINDOWS /DSTRICT
    set LFLAGS=
)

mkdir "%OUTDIR%" 2>nul

echo === Building Steven [%CONFIG%] ===
echo SDK: %GAMEBRYO_SDK%
echo Libs: %LIBDIR%

REM Compile
cl.exe /nologo /c /EHs- /W3 /Zc:forScope ^
    /FI"NiBuildConfiguration.h" ^
    /I"%SRCDIR%" /I"%INCDIR%" ^
    %CFLAGS% ^
    /Fo"%OUTDIR%\\" ^
    "%SRCDIR%\StevenApp.cpp" ^
    "%SRCDIR%\StevenApp_Win32.cpp"

if errorlevel 1 (
    echo COMPILE FAILED
    exit /b 1
)

REM Link
link.exe /nologo /SUBSYSTEM:WINDOWS ^
    /LIBPATH:"%LIBDIR%" ^
    /NODEFAULTLIB:libci.lib ^
    %LFLAGS% ^
    /OUT:"%OUTDIR%\Steven.exe" ^
    "%OUTDIR%\StevenApp.obj" ^
    "%OUTDIR%\StevenApp_Win32.obj" ^
    NiSystem.lib NiMain.lib NiDX9Renderer.lib ^
    NiApplication.lib NiVisualTracker.lib NiInput.lib ^
    user32.lib gdi32.lib advapi32.lib shell32.lib ^
    d3d9.lib d3dx9.lib dinput8.lib dxguid.lib

if errorlevel 1 (
    echo LINK FAILED
    exit /b 1
)

echo === Build succeeded: %OUTDIR%\Steven.exe ===
