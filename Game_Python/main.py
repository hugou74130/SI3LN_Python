import pygame
import os
import sys
import asyncio

try:
    from game import Game
except ImportError:
    print("Attention: Assurez-vous que le code de la classe Game est soit dans ce fichier, soit dans 'game.py'.")
    sys.exit(1)


def _is_wasm():
    """Detect if we are running under Pygbag / Emscripten / WASM."""
    # 1. Emscripten sets sys.platform to 'emscripten'
    if sys.platform == 'emscripten':
        return True
    # 2. Check version string for emscripten marker
    if 'emscripten' in sys.version.lower():
        return True
    # 3. Pygbag injects RUNNING_IN_PYGBAG via JS → accessible from Python
    try:
        from js import window  # noqa: F401  (only available under Pyodide / Pygbag)
        if hasattr(window, 'RUNNING_IN_PYGBAG') or window.RUNNING_IN_PYGBAG:
            return True
    except ImportError:
        pass
    # 4. Environment variable (set by Dockerfile or shell wrapper)
    if os.environ.get('RUNNING_IN_PYGBAG') or os.environ.get('PYGBAG'):
        return True
    # 5. platform.machine() on wasm32 / wasm64
    try:
        import platform
        m = platform.machine().lower()
        if 'wasm' in m or 'emscripten' in m:
            return True
    except Exception:
        pass
    return False


# ── MUST set SDL drivers BEFORE pygame.init() ──────────────────────────────
_is_wasm_env = _is_wasm()
if _is_wasm_env:
    # Pygbag provides its own SDL2 video/audio backend via Emscripten;
    # do NOT override with 'dummy' or the canvas stays blank.
    pass


async def main():
    pygame.init()
    game = Game(wasm=_is_wasm_env)
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
