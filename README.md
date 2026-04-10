# Steven

Reimplementation of the Shin Megami Tensei: Imagine Online client using the Gamebryo 2.3 engine.

## Requirements

- **Visual C++ 2005** (MSVC 8.0 / VC80) — cl.exe + link.exe. VS2005 Express Edition works.
- **Gamebryo 2.3 Evaluation SDK** — provides engine headers and precompiled VC80 libs
- **DirectX 9 SDK** — D3D9 headers and libs (included in Windows SDK 6.0+)

Can run under Wine on Linux — only the compiler and linker need to work, not the IDE.

## Build

### Command line (preferred)

```bat
set GAMEBRYO_SDK=C:\path\to\Gamebryo_2.3_eval\SDK\DEST_APP_PATH
build.cmd release
```

### Visual Studio 2005

1. Set `GAMEBRYO_SDK` environment variable
2. Open `build/VC80/Steven.sln`
3. Build Release configuration

### Wine (Linux)

```bash
# After installing VS2005 Express under Wine:
export GAMEBRYO_SDK="Z:/home/nam/Documents/smtimagine/Gamebryo_2.3_eval/SDK/DEST_APP_PATH"
wine cmd /c build.cmd release
```

## Current Status

**Milestone 0**: Gamebryo application shell — D3D9 window, orbit camera, colored triangle.
