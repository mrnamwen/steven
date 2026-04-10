#!/bin/bash
# Build Gamebryo 2.3 engine libraries from source using VC71 under Wine
# Produces .lib files in $OUT_LIB with NO timelock
set -euo pipefail

TOOLDIR="/home/nam/Documents/smtimagine/tools/vc71"
GB_SRC="/home/nam/Documents/smtimagine/Gamebryo_2.3"
PSDK="/home/nam/Documents/smtimagine/tools/psdk"
OUT_LIB="/home/nam/Documents/smtimagine/tools/gamebryo_libs"
OUT_OBJ="/tmp/gamebryo_build"

# Wine path converter
W() { echo "Z:${1//\//\\\\}"; }

CL="$TOOLDIR/cl.exe"
LIB="$TOOLDIR/lib.exe"

COMMON_FLAGS="/nologo /c /EHs- /W3 /O2 /MD"
COMMON_DEFS="/DNIRELEASE /DNDEBUG /DWIN32 /D_WINDOWS /DSTRICT"
COMMON_DEFS="$COMMON_DEFS /DNI_USE_MEMORY_MANAGEMENT=1"

W_CRT="$(W "$TOOLDIR/include")"
W_PSDK="$(W "$PSDK/include")"

mkdir -p "$OUT_LIB" "$OUT_OBJ"

compile_lib() {
    local LIB_NAME="$1"
    local SRC_DIR="$2"
    shift 2
    local EXTRA_INCLUDES=("$@")

    echo "=== Building $LIB_NAME ==="

    local OBJ_DIR="$OUT_OBJ/$LIB_NAME"
    mkdir -p "$OBJ_DIR"

    # Collect all .cpp files (main dir + Win32 subdir)
    local SOURCES=()
    for f in "$SRC_DIR"/*.cpp; do
        [ -f "$f" ] && SOURCES+=("$f")
    done
    if [ -d "$SRC_DIR/Win32" ]; then
        for f in "$SRC_DIR/Win32"/*.cpp; do
            [ -f "$f" ] && SOURCES+=("$f")
        done
    fi

    # Build include path
    local INC_FLAGS="/I$(W "$SRC_DIR") /I$(W "$SRC_DIR/Win32") /I$W_CRT /I$W_PSDK"
    for inc in "${EXTRA_INCLUDES[@]}"; do
        INC_FLAGS="$INC_FLAGS /I$(W "$inc")"
    done

    # Compile each source file
    local OBJ_FILES=()
    local FAILED=0
    for src in "${SOURCES[@]}"; do
        local base=$(basename "${src%.cpp}")
        local obj="$OBJ_DIR/${base}.obj"
        local w_obj="$(W "$obj")"
        local w_src="$(W "$src")"

        if [ -f "$obj" ] && [ "$obj" -nt "$src" ]; then
            OBJ_FILES+=("$w_obj")
            continue
        fi

        echo "  CC $base.cpp"
        if ! wine "$CL" $COMMON_FLAGS $COMMON_DEFS \
            $INC_FLAGS \
            "/FINiBuildConfiguration.h" \
            "/Fo$w_obj" "$w_src" \
            2>&1 | grep -v "libEGL\|pci id\|egl:\|warning C4068\|^$" | grep -q "error"; then
            OBJ_FILES+=("$w_obj")
        else
            wine "$CL" $COMMON_FLAGS $COMMON_DEFS \
                $INC_FLAGS \
                "/FINiBuildConfiguration.h" \
                "/Fo$w_obj" "$w_src" \
                2>&1 | grep -v "libEGL\|pci id\|egl:\|^$" | grep "error" | head -3
            FAILED=$((FAILED + 1))
        fi
    done

    if [ $FAILED -gt 0 ]; then
        echo "  WARNING: $FAILED files failed to compile"
    fi

    # Create static library
    if [ ${#OBJ_FILES[@]} -gt 0 ]; then
        local w_lib="$(W "$OUT_LIB/$LIB_NAME.lib")"
        echo "  LIB -> $LIB_NAME.lib (${#OBJ_FILES[@]} objects)"
        wine "$LIB" /nologo "/OUT:$w_lib" "${OBJ_FILES[@]}" \
            2>&1 | grep -v "libEGL\|pci id\|egl:"
        ls -lh "$OUT_LIB/$LIB_NAME.lib"
    fi
    echo ""
}

# === Build order (dependency chain) ===

# 1. NiSystem - no engine deps
compile_lib "NiSystem" "$GB_SRC/CoreLibs/NiSystem"

# 2. NiMain - depends on NiSystem
compile_lib "NiMain" "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32"

# 3. NiFloodgate - depends on NiSystem, NiMain
compile_lib "NiFloodgate" "$GB_SRC/CoreLibs/NiFloodgate" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32" \
    "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiMain/Win32"

# 4. NiDX9Renderer - depends on NiSystem, NiMain, + DX9 SDK
compile_lib "NiDX9Renderer" "$GB_SRC/CoreLibs/NiDX9Renderer" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32" \
    "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiMain/Win32" \
    "$PSDK/include"

# 5. NiAnimation - depends on NiSystem, NiMain
compile_lib "NiAnimation" "$GB_SRC/CoreLibs/NiAnimation" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32" \
    "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiMain/Win32"

# 6. NiCollision - depends on NiSystem, NiMain
compile_lib "NiCollision" "$GB_SRC/CoreLibs/NiCollision" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32" \
    "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiMain/Win32"

# 7. NiParticle - depends on NiSystem, NiMain
compile_lib "NiParticle" "$GB_SRC/CoreLibs/NiParticle" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32" \
    "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiMain/Win32"

# 8. NiInput (AppFrameworks utility)
compile_lib "NiInput" "$GB_SRC/AppFrameworks/UtilityLibs/NiInput" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32" \
    "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiMain/Win32" \
    "$PSDK/include"

# 9. NiVisualTracker
compile_lib "NiVisualTracker" "$GB_SRC/AppFrameworks/UtilityLibs/NiVisualTracker" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32" \
    "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiMain/Win32"

# 10. NiApplication
compile_lib "NiApplication" "$GB_SRC/AppFrameworks/NiApplication" \
    "$GB_SRC/CoreLibs/NiSystem" \
    "$GB_SRC/CoreLibs/NiSystem/Win32" \
    "$GB_SRC/CoreLibs/NiMain" \
    "$GB_SRC/CoreLibs/NiMain/Win32" \
    "$GB_SRC/AppFrameworks/UtilityLibs/NiInput" \
    "$GB_SRC/AppFrameworks/UtilityLibs/NiVisualTracker" \
    "$PSDK/include"

echo "==========================================="
echo "Build complete. Libraries in: $OUT_LIB"
echo "==========================================="
ls -lhS "$OUT_LIB/"*.lib 2>/dev/null
