"""
REST API client for SI3LN Python game.

Desktop mode  : uses `requests` (sync HTTP)
Browser/Pygbag: requests is unavailable; API calls silently return None
                (scores/sessions are disabled in browser – they go through the
                 frontend JS layer instead)
"""

import os
import sys
import json
import base64
import platform

# ── Browser detection ─────────────────────────────────────────────────────────
# Pygbag sets sys.platform = 'emscripten' when running in the browser
IS_BROWSER = sys.platform in ("emscripten", "wasi")


def _browser_win():
    """Return the window that owns our JS bridges.

    Pygbag runs inside an iframe on /game/index.html.
    platform.window = the iframe's window; the bridges (SI3LN_*) are
    defined on the *parent* window — accessible via window.parent because
    the iframe uses sandbox="allow-same-origin".
    Falls back to platform.window when not in an iframe (window.parent === window).
    """
    win = platform.window
    parent = getattr(win, "parent", win)
    return parent if parent is not None else win

# ── requests import (desktop only) ───────────────────────────────────────────
if not IS_BROWSER:
    try:
        import requests as _requests
        _HAS_REQUESTS = True
    except ImportError:
        _HAS_REQUESTS = False
else:
    _HAS_REQUESTS = False

# ── Config ────────────────────────────────────────────────────────────────────
try:
    from constants import API_URL, API_TOKEN
except ImportError:
    API_URL   = os.environ.get("SI3LN_API_URL", "http://localhost:8000")
    API_TOKEN = os.environ.get("SI3LN_TOKEN", "")


def _jwt_field(token: str, field: str):
    """Decode a single field from a JWT payload without verification."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload).decode())
        return data.get(field)
    except Exception:
        return None


class APIClient:
    """Thin wrapper around the SI3LN Django-Ninja REST API."""

    def __init__(self):
        self._token: str = ""
        self._player_id: int | None = None
        self._username: str = ""
        self._session_id: int | None = None
        self._load_token()

    # ── Token management ──────────────────────────────────────────────────────

    def _load_token(self):
        """Load JWT from env var (desktop) or window.SI3LN_JWT_TOKEN (browser)."""
        token = API_TOKEN or os.environ.get("SI3LN_TOKEN", "")

        if not token and IS_BROWSER:
            try:
                token = getattr(_browser_win(), "SI3LN_JWT_TOKEN", "") or ""
            except Exception:
                token = ""

        if token:
            self.set_token(token)

    def set_token(self, token: str):
        self._token  = token
        self._player_id = _jwt_field(token, "player_id")
        self._username  = _jwt_field(token, "username") or ""

    def is_authenticated(self) -> bool:
        return bool(self._token and self._player_id)

    def get_username(self) -> str:
        return self._username

    def get_player_id(self):
        return self._player_id

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _get(self, path: str):
        if not _HAS_REQUESTS:
            return None
        try:
            r = _requests.get(
                f"{API_URL}{path}", headers=self._headers(), timeout=5
            )
            return r.json() if r.ok else None
        except Exception:
            return None

    def _post(self, path: str, data: dict):
        if not _HAS_REQUESTS:
            return None
        try:
            r = _requests.post(
                f"{API_URL}{path}", json=data, headers=self._headers(), timeout=5
            )
            return r.json() if r.ok else None
        except Exception:
            return None

    def _patch(self, path: str, data: dict):
        if not _HAS_REQUESTS:
            return None
        try:
            r = _requests.patch(
                f"{API_URL}{path}", json=data, headers=self._headers(), timeout=5
            )
            return r.json() if r.ok else None
        except Exception:
            return None

    # ── Public API ────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> bool:
        """Authenticate and store JWT. Returns True on success."""
        result = self._post("/api/auth/login", {
            "username": username,
            "password": password,
        })
        if result and "token" in result:
            self.set_token(result["token"])
            return True
        return False

    def start_session(self, world_id: int = 1) -> int | None:
        """Start a game session. Returns session id or None."""
        if not self.is_authenticated():
            return None
        result = self._post("/api/game/sessions", {
            "world_id":  world_id,
            "player_id": self._player_id,
        })
        if result and "id" in result:
            self._session_id = result["id"]
            return self._session_id
        return None

    def end_session(
        self,
        score: int = 0,
        level: int = 1,
        enemies_killed: int = 0,
        duration: int = 0,
    ):
        """End the current session with results. Returns response or None."""
        if not self.is_authenticated() or not self._session_id:
            return None
        result = self._patch(f"/api/game/sessions/{self._session_id}", {
            "score":          score,
            "level_reached":  level,
            "enemies_killed": enemies_killed,
            "duration_seconds": duration,
            "completed":      True,
        })
        self._session_id = None
        return result

    def submit_leaderboard(
        self,
        score: int = 0,
        world_id: int = 1,
        level_id: int = 1,
        character_used: str = "",
        duration_sec: int = 0,
        accuracy_pct: float = 0.0,
        enemies_killed: int = 0,
        powerups_used: int = 0,
        bullets_fired: int = 0,
        replay_hash: str = "",
    ) -> dict | None:
        """Submit a completed run to the persistent leaderboard. Returns server response or None."""
        if not self.is_authenticated():
            return None
        payload = {
            "score": score,
            "world_id": world_id,
            "level_id": level_id,
            "character_used": character_used,
            "duration_sec": duration_sec,
            "accuracy_pct": accuracy_pct,
            "enemies_killed": enemies_killed,
            "powerups_used": powerups_used,
            "bullets_fired": bullets_fired,
            "replay_hash": replay_hash,
        }
        # Link to the current session if one was started
        if self._session_id is not None:
            payload["session_id"] = self._session_id
        # In browser mode (Pygbag), HTTP requests are unavailable.
        # Delegate submission to the parent HTML page via platform.window.
        if IS_BROWSER:
            try:
                fn = getattr(_browser_win(), "SI3LN_submit_score", None)
                if fn:
                    fn(json.dumps(payload))
            except Exception:
                pass
            return None

        return self._post("/api/game/leaderboard/submit", payload)

    def get_leaderboard_global(self, world: int | None = None, limit: int = 50) -> list:
        """Return top global scores from persistent leaderboard."""
        if IS_BROWSER:
            try:
                win = _browser_win()
                cache = getattr(win, "SI3LN_LEADERBOARD_CACHE", None)
                if cache:
                    data = json.loads(str(cache))
                    entries = data if isinstance(data, list) else data.get("entries", [])
                    if world is not None:
                        entries = [e for e in entries if e.get("world_id") == world]
                    return entries[:limit]
                # Cache miss — trigger a fetch for next call
                fn = getattr(win, "SI3LN_fetch_leaderboard", None)
                if fn:
                    fn(world, limit)
            except Exception:
                pass
            return []

        params = f"limit={limit}"
        if world is not None:
            params += f"&world={world}"
        result = self._get(f"/api/game/leaderboard/global?{params}")
        if isinstance(result, dict) and "entries" in result:
            return result["entries"]
        return []

    def get_leaderboard_player(self, player_id: int | None = None) -> dict | None:
        """Return a player's full history + personal bests."""
        pid = player_id or self._player_id
        if pid is None:
            return None
        return self._get(f"/api/game/leaderboard/player/{pid}")

    def get_leaderboard_nearby(self, player_id: int | None = None, radius: int = 5) -> dict | None:
        """Return players ranked near the target player."""
        pid = player_id or self._player_id
        if pid is None:
            return None
        return self._get(f"/api/game/leaderboard/nearby?player={pid}&radius={radius}")

    def get_leaderboard(self, limit: int = 10) -> list:
        """Return list of top scores (legacy endpoint). Falls back to empty list on error."""
        result = self._get(f"/api/game/leaderboard?limit={limit}")
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "results" in result:
            return result["results"]
        return []

    def get_player(self) -> dict | None:
        """Return player profile dict or None."""
        if not self._player_id:
            return None
        return self._get(f"/api/game/players/{self._player_id}")

    def unlock_character(self, character_idx: int) -> dict | None:
        """Unlock a character via the API. Returns response or None."""
        if not self.is_authenticated():
            return None
        return self._post(f"/api/game/players/{self._player_id}/unlock-character", {
            "character_idx": character_idx,
        })

    def grant_achievement(self, achievement_name: str) -> dict | None:
        """Grant an achievement via the API. Returns response or None."""
        if not self.is_authenticated():
            return None
        return self._post(f"/api/game/players/{self._player_id}/grant-achievement", {
            "achievement_name": achievement_name,
        })


# ── Singleton ─────────────────────────────────────────────────────────────────
api_client = APIClient()
