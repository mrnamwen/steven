# Steven

Reimplementation of the Shin Megami Tensei: Imagine Online client using the Gamebryo 2.3 engine.

## Requirements

- **Windows XP or later** (D3D9 target)
- **Visual Studio .NET 2003** (MSVC 7.1) — required for Gamebryo 2.3 VC71 libs
- **Gamebryo 2.3 Evaluation SDK** — set the `GAMEBRYO_SDK` environment variable to the SDK root:
  ```
  set GAMEBRYO_SDK=C:\path\to\Gamebryo_2.3_eval\SDK\DEST_APP_PATH
  ```

## Build

1. Set the `GAMEBRYO_SDK` environment variable
2. Open `build/VC71/Steven.sln` in Visual Studio .NET 2003
3. Build the Release configuration
4. The executable will be at `build/VC71/Release/Steven.exe`

## Current Status

**Milestone 0**: Gamebryo application shell — D3D9 window, orbit camera, colored triangle.
