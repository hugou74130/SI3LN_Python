# Stage 3: Technical Documentation — ARCAD3X

**Project:** ARCAD3X (SI3LN) — Arcade Analytics Platform  
**Author:** Hugo Ramos — Game Client & Integration Lead  
**Institution:** Holberton School  
**Date:** May 2025  
**Version:** 2.0  
**Repository Code:** `https://github.com/hugou74130/SI3LN`  
**Documentation:** `https://github.com/hugou74130/arcad3x-stage3-private`  
**Game Engine:** `Game_Python/` (Pygame + Pygbag/WASM)  
**Backend API:** `api/` (Django + Django Ninja)  
**Web Dashboard:** `web_dashboard/` (Vanilla JS SPA served by nginx)  
**Orchestration:** `Docker/docker-compose.yml` (db · redis · api · frontend)

---

## Executive Summary

This document presents the technical architecture and implementation details of the **ARCAD3X game client**, a Python/Pygame arcade shooter with API integration, developed as part of the Holberton School curriculum. The game client supports offline-first gameplay with server synchronization, cross-platform controls (keyboard and touch), and responsive resolution scaling. This documentation covers user stories, system architecture, component design, sequence diagrams, API specifications, source control management, quality assurance plans, and technical justifications.

---

## Table of Contents

1. [User Stories & Mockups](#1-user-stories--mockups)
2. [System Architecture](#2-system-architecture)
3. [Components, Classes & Database Design](#3-components-classes--database-design)
4. [High-Level Sequence Diagrams](#4-high-level-sequence-diagrams)
5. [External & Internal APIs](#5-external--internal-apis)
6. [SCM & QA Plans](#6-scm--qa-plans)
7. [Technical Justifications](#7-technical-justifications)
8. [Deployment Plan](#8-deployment-plan)
9. [Appendix A: Risk Register](#appendix-a-risk-register)

---

## 1. User Stories & Mockups

### 1.1 User Stories (MoSCoW Prioritization)

All user stories follow the standard format: *"As a [user type], I want to [perform an action], so that [achieve a goal]."* Stories are prioritized using the MoSCoW method (Must, Should, Could, Won't Have) to ensure alignment with the Minimum Viable Product (MVP).

#### 1.1.1 Must Have (M) — MVP Core

These stories represent the minimum functionality required for the product to be usable. Without these, the arcade experience does not exist.

| ID | User Story | Mockup Ref |
|:---|:---|:---|
| **US-M1** | **As a** guest player, **I want to** launch the game immediately without creating an account, **so that** I can try the arcade experience with zero friction. | [Main Menu](#mockup-01-main-menu) |
| **US-M2** | **As a** registered player, **I want to** log in with my username and password, **so that** my scores are saved and synced to the server. | [Login](#mockup-02-login) |
| **US-M3** | **As a** player, **I want to** shoot enemies, dodge bullets, and collect bonuses (shield, mega-shot), **so that** I experience classic arcade tension. | [Gameplay](#mockup-06-gameplay) |
| **US-M4** | **As a** player, **I want to** see my score, lives, and level displayed in real-time during gameplay, **so that** I can track my performance. | [Gameplay](#mockup-06-gameplay) |
| **US-M5** | **As a** player, **I want to** submit my final score to the API when the game ends, **so that** it appears on the global leaderboard. | [Game Over](#mockup-07-game-over) |

**Rationale:** The Must Have set covers the complete core loop: launch (US-M1) → authenticate (US-M2) → play (US-M3) → track progress (US-M4) → persist results (US-M5). This loop is non-negotiable for any arcade game.

#### 1.1.2 Should Have (S) — High Value, Short-Term

These stories add significant value to the MVP and differentiate the product from a basic tech demo.

| ID | User Story | Mockup Ref |
|:---|:---|:---|
| **US-S1** | **As a** player, **I want to** select between 5 distinct game worlds (Space, Desert, Forest, Marine, Apocalyptic) with unique visuals and enemy patterns, **so that** the gameplay stays varied. | [Level Selector](#mockup-05-level-selector) |
| **US-S2** | **As a** player, **I want to** choose from 7+ playable characters (sprite selection), **so that** I can personalize my ship. | [Character Select](#mockup-04-character-select) |
| **US-S3** | **As a** player, **I want to** play on both desktop (keyboard) and mobile (touch controls), **so that** the game is accessible everywhere. | [Gameplay](#mockup-06-gameplay) |
| **US-S4** | **As a** player, **I want to** toggle fullscreen and adjust settings via `config.ini`, **so that** I can optimize the experience for my screen. | [Main Menu](#mockup-01-main-menu) |

**Rationale:** These features provide variety (US-S1, US-S2) and accessibility (US-S3, US-S4). They are scheduled for the first release sprint following MVP validation.

#### 1.1.3 Could Have (C) — Nice-to-Have

These stories add polish and strategic depth. They will be implemented if sprint velocity permits.

| ID | User Story | Mockup Ref |
|:---|:---|:---|
| **US-C1** | **As a** player, **I want to** use special attacks and suffer debuffs (frozen, blinded, rooted), **so that** the gameplay has strategic depth. | [Gameplay](#mockup-06-gameplay) |
| **US-C2** | **As a** player, **I want to** view a local top-20 leaderboard between sessions, **so that** I can compete against myself and friends on the same machine. | [Profile](#mockup-09-profile) |
| **US-C3** | **As a** player, **I want to** see explosion effects and screen shake when hitting enemies, **so that** the combat feels impactful. | [Gameplay](#mockup-06-gameplay) |

**Rationale:** These are quality-of-life improvements. US-C2 addresses the non-functional requirement for local competition, while US-C1 and US-C3 enhance game feel.

#### 1.1.4 Won't Have (W) — Post-MVP / V2

These stories are explicitly excluded from the current scope to maintain focus and prevent scope creep.

| ID | User Story | Reason |
|:---|:---|:---|
| **US-W1** | **As a** player, **I want to** play multiplayer duels in real-time, **so that** I can compete directly against friends. | WebSocket/RTC complexity exceeds MVP timeline. |
| **US-W2** | **As a** player, **I want to** stream my gameplay with an OBS overlay showing live stats, **so that** my viewers can follow my performance. | Streaming API integration is not required for academic deliverable. |
| **US-W3** | **As a** player, **I want to** export my gameplay data as CSV, **so that** I can analyze it externally. | Data export is a V2 analytics feature. |

**Rationale:** Marking scope boundaries explicitly prevents feature creep and ensures the team delivers a shippable MVP within the academic timeline.

---

### 1.2 Mockups — Game Screens

The following mockups represent the nine primary screens of the ARCAD3X game client. All screens are rendered at the reference resolution of 1280×720 pixels.

#### Mockup 01: Main Menu

![Main Menu](mockups/01_main_menu.png)

| Element | Description | User Story |
|:---|:---|:---|
| Title "SI3LN" | Game logo, arcade-style typography | US-M1 |
| START / PLAY buttons | Launch gameplay or level selector | US-M1 |
| CONNEXION / INSCRIPTION | Navigate to authentication screens | US-M2 |
| QUITTER / AIDE | Exit game or display help popup | US-M1 |
| Profile icon (top-right) | Quick access to player profile | US-S2 |

**Type:** Real screenshot captured from the running Pygame application.

---

#### Mockup 02: Login

![Login](mockups/02_login.png)

| Element | Description | User Story |
|:---|:---|:---|
| Username input field | Text entry for player identifier | US-M2 |
| Password input field | Masked entry for credentials | US-M2 |
| "SE CONNECTER" button | Submit credentials to AuthSystem | US-M2 |
| "JOUER EN INVITÉ" button | Skip authentication, play offline | US-M1 |
| "Créer un compte" link | Navigate to registration screen | US-M2 |

**Type:** Wireframe based on actual Pygame UI component dimensions and styling.

---

#### Mockup 03: Register

![Register](mockups/03_register.png)

| Element | Description | User Story |
|:---|:---|:---|
| Username input field | Unique player identifier | US-M2 |
| Email input field | Contact address for account recovery | US-M2 |
| Password / Confirm fields | Credential pair with validation | US-M2 |
| "CRÉER MON COMPTE" button | Submit new account to API | US-M2 |
| "RETOUR" button | Return to login screen | US-M2 |

**Type:** Wireframe based on actual Pygame UI component dimensions and styling.

---

#### Mockup 04: Character Select

![Character Select](mockups/04_character_select.png)

| Element | Description | User Story |
|:---|:---|:---|
| Sprite grid (8 slots) | Display of available ship sprites from `assets/players/` | US-S2 |
| Selection highlight | Visual feedback on chosen character | US-S2 |
| "CONFIRMER" button | Proceed to level selection with chosen character | US-S2 |

**Type:** Asset composition using real game sprites.

---

#### Mockup 05: Level Selector

![Level Selector](mockups/05_level_selector.png)

| Element | Description | User Story |
|:---|:---|:---|
| World cards (5) | Space, Desert, Forest, Marine, Apocalyptic | US-S1 |
| Level dots per world | Progression indicators (locked/unlocked) | US-S1 |
| World description panel | Brief text about selected world's theme | US-S1 |

**Type:** Asset composition using real game backgrounds.

---

#### Mockup 06: Gameplay

![Gameplay](mockups/06_gameplay.png)

| Element | Description | User Story |
|:---|:---|:---|
| Player ship | Controllable sprite (keyboard or touch) | US-M3 |
| Enemy wave | Space-Invaders style patrol AI | US-M3 |
| Bullets (player + enemy) | Projectile collision system | US-M3 |
| HUD (score, lives, level) | Real-time performance tracking | US-M4 |
| Touch buttons (mobile) | Fire, shield, mega-shot on-screen controls | US-S3 |

**Type:** Asset composition using real `background_space.jpg` and game sprites.

---

#### Mockup 07: Game Over

![Game Over](mockups/07_game_over.png)

| Element | Description | User Story |
|:---|:---|:---|
| Final score display | Total points accumulated during session | US-M5 |
| Level reached | Highest level attained before game over | US-M5 |
| Duration | Elapsed time of the session | US-M5 |
| Global rank | Leaderboard position after API sync | US-M5 |
| "RÉESSAYER" / "MENU" buttons | Replay or return to main menu | US-M1 |

**Type:** Wireframe based on actual Pygame UI component dimensions and styling.

---

#### Mockup 08: Level Win

![Level Win](mockups/08_level_win.png)

| Element | Description | User Story |
|:---|:---|:---|
| Completion score | Points earned during the level | US-M4 |
| Bonus display | Survival bonus and multipliers | US-C3 |
| "NIVEAU SUIVANT" button | Proceed to next level in world progression | US-S1 |
| "MENU" button | Return to main menu | US-M1 |

**Type:** Wireframe based on actual Pygame UI component dimensions and styling.

### 1.3 Mockup Completeness Matrix

| Screen | Mockup Available | Format | Coverage |
|:---|:---:|:---|:---|
| Main Menu | ✅ | Real screenshot | 100% |
| Login | ✅ | Wireframe | 100% |
| Register | ✅ | Wireframe | 100% |
| Character Select | ✅ | Asset composition | 100% |
| Level Selector | ✅ | Asset composition | 100% |
| Gameplay | ✅ | Asset composition | 100% |
| Game Over | ✅ | Wireframe | 100% |
| Level Win | ✅ | Wireframe | 100% |
| Profile | ✅ | Wireframe | 100% |

**Total coverage:** 9/9 screens (100%).

---

## 2. System Architecture

### 2.1 High-Level Architecture Diagram

The following diagram illustrates the complete system architecture, from the player-facing game client through the API layer to the persistence tier.

```mermaid
graph TD
    subgraph Client["Game Client — Python / Pygame / Pygbag"]
        G[Game State Machine]
        E[Entities]
        A[AuthSystem]
        S[ScoreManager]
        C[APIClient]
        R[ResolutionManager]
        U[UI Components]
    end

    subgraph API["API Backend — Django Ninja"]
        Auth["/api/auth/*"]
        GameAPI["/api/game/*"]
        Docs["/api/docs"]
    end

    subgraph Data["Persistence — PostgreSQL 15"]
        DB[(Database)]
    end

    Player["Player"] -->|Keyboard / Touch| G
    G --> E
    G --> A
    G --> S
    G --> C
    G --> R
    G --> U
    C -->|HTTP + Bearer JWT| Auth
    C -->|HTTP + Bearer JWT| GameAPI
    Auth -->|Django ORM| DB
    GameAPI -->|Django ORM| DB
    Docs -->|OpenAPI Schema| GameAPI

    style Client fill:#0a0a1a,stroke:#4fc3f7,stroke-width:2px,color:#fff
    style API fill:#0a1a0a,stroke:#66bb6a,stroke-width:2px,color:#fff
    style Data fill:#1a0a1a,stroke:#ab47bc,stroke-width:2px,color:#fff
    style Player fill:#1a1a2e,stroke:#ffd54f,stroke-width:2px,color:#fff
```

**Legend:**
- 🔵 Blue border: Game Client layer (Python/Pygame)
- 🟢 Green border: API Backend layer (Django Ninja)
- 🟣 Purple border: Persistence layer (PostgreSQL)
- 🟡 Yellow border: External actor (Player)

### 2.2 Architectural Patterns

| Pattern | Implementation | Functional Requirement | Non-Functional Requirement |
|:---|:---|:---|:---|
| **State Machine** | `self.state` string with per-state `handle_events()`, `update()`, `draw()` branching | US-M1: discrete game screens | Maintainability: clean separation of concerns |
| **Game Loop** | `while self.running: handle_events() → update() → draw() → clock.tick(FPS)` | US-M3: real-time gameplay | NFR-Performance: 60 FPS target |
| **Entity-Component (Lightweight)** | `pygame.sprite.Sprite` subclasses with built-in collision detection | US-M3: enemy/bullet interactions | NFR-Performance: optimized sprite groups |
| **Resolution Manager** | Fixed 1280×720 reference canvas scaled to any window size | US-S3: cross-platform support | NFR-Usability: responsive layout |
| **API Facade** | `APIClient` wraps `requests` with JWT auto-injection | US-M5: score submission | NFR-Security: token encapsulation |
| **Local-First Auth** | `AuthSystem` stores users in local JSON; syncs with server when online | US-M1: offline play | NFR-Reliability: graceful degradation |

**NFR Definitions:**
- **NFR-Performance:** The game shall maintain a minimum of 60 frames per second on reference hardware.
- **NFR-Usability:** The game shall be playable on both desktop (keyboard) and mobile (touch) without code changes.
- **NFR-Security:** API communications shall use JWT Bearer tokens with HS256 encryption.
- **NFR-Reliability:** The game shall function in offline mode, queueing data for synchronization when connectivity is restored.

---

## 3. Components, Classes & Database Design

### 3.1 Game Client Component Hierarchy

```
Game_Python/
├── game.py              → Game class (state machine, main loop, event handling)
│                          ├─ load_assets()       → fonts, backgrounds, players, enemies, bullets
│                          ├─ create_ui()         → all Button/InputField instances per state
│                          ├─ handle_events()      → pygame event polling, touch tracking
│                          ├─ update()             → per-frame game logic (collisions, spawning)
│                          ├─ draw()               → render to reference canvas, then scale
│                          ├─ start_gameplay()    → init player, enemies, bullets for a level
│                          ├─ end_game()          → calculate score, submit to API, show Game Over
│                          └─ _transform_event() → mouse→reference coordinate remapping
│
├── entities.py          → Sprite subclasses
│                          ├─ Player             → move(), update(keys), move_toward(touch)
│                          ├─ Enemy              → update() patrol AI, shoot cooldown
│                          ├─ Bullet             → linear movement, off-screen cleanup
│                          ├─ Explosion          → animated sprite sheet frames
│                          ├─ Bonus              → shield / mega-shot pickups
│                          └─ SpecialAttack       → AOE / piercing attack entities
│
├── auth.py              → AuthSystem class
│                          ├─ register()         → username validation, password hash, JSON save
│                          ├─ login()            → credential check, set current_user
│                          ├─ login_as_guest()  → no score saving, character selection allowed
│                          ├─ logout()           → clear session
│                          └─ update_user_data() → local JSON persistence
│
├── scores.py            → ScoreManager class
│                          ├─ add_score()        → insert, sort, keep top 20, save JSON
│                          ├─ get_top_scores()    → return N best entries
│                          ├─ is_high_score()     → threshold check for top 20
│                          └─ get_rank()          → compute hypothetical rank
│
├── api_client.py        → APIClient class
│                          ├─ set_token()          → decode JWT payload (player_id, username)
│                          ├─ is_authenticated()    → token presence check
│                          ├─ create_session()     → POST /api/game/sessions
│                          ├─ submit_leaderboard()  → POST /leaderboard/submit (browser: SI3LN_submit_score bridge)
│                          ├─ submit_progress()     → PATCH /progress (browser: SI3LN_save_progress bridge)
│                          ├─ get_leaderboard_global() → GET /leaderboard/global (browser: reads cache)
│                          └─ _post/_get/_patch()   → HTTP with Bearer JWT, 5s timeout (desktop only)
│
├── level_selector.py    → LevelSelector class
│                          ├─ draw()             → world carousel + level dots
│                          ├─ handle_event()      → click detection, world selection
│                          └─ is_level_unlocked() → progression lock logic
│
├── profile.py           → ProfileScreen class
│                          ├─ draw()             → stats cards, avatar, bio
│                          ├─ handle_event()     → navigation buttons
│                          └─ refresh_stats()     → reload from AuthSystem
│
├── ui_components.py     → Reusable widgets
│                          ├─ Button             → hover/click states, rounded rect
│                          ├─ InputField         → text entry, password masking, cursor
│                          ├─ ProfileIcon        → circular clipped avatar
│                          ├─ Panel              → semi-transparent background panel
│                          └─ PopUp              → scrollable text modal (Help, About)
│
├── constants.py         → Configuration constants (no classes)
│                          ├─ WORLDS dict        → 5 worlds with backgrounds, colors, enemy counts
│                          ├─ Game states         → STATE_MAIN_MENU … STATE_HELP
│                          ├─ Gameplay values     → MAX_LIVES, PLAYER_SPEED, ENEMY_SPEED, FPS
│                          ├─ WORLD_IDS mapping   → name → DB primary key
│                          └─ API_URL / API_TOKEN → env-driven endpoint config
│
├── resolution_manager.py → ResolutionManager class
│                          ├─ canvas             → 1280×720 reference surface
│                          ├─ screen_to_ref()    → remap mouse coords
│                          ├─ present()           → scale + center onto real display
│                          └─ is_portrait         → boolean layout branch
│
├── utils.py             → Utility functions
│                          ├─ load_image()       → resize + colorkey
│                          ├─ draw_text()         → anti-aliased font render
│                          ├─ load_enemy_images() → per-world enemy sprite sheets
│                          └─ create_bullet_surface() → gradient bullet texture
│
└── config.ini           → User-editable settings
                           ├─ [Display]          → resolution, fullscreen, vsync
                           ├─ [Gameplay]         → difficulty, lives count
                           ├─ [Audio]            → music/sfx volume
                           └─ [Controls]         → key remapping
```

### 3.2 Key Classes — Game Client Specification

The following tables document each class with its attributes, methods, types, and descriptions.

#### 3.2.1 Player Class (`entities.py`)

| Attribute | Type | Description | Mandatory |
|:---|:---|:---|:---:|
| `speed` | `int` | Pixels per frame (default: 8) | ✅ |
| `rect` | `pygame.Rect` | Bounding box for collision detection | ✅ |
| `image` | `pygame.Surface` | Sprite graphic (8-directional or static) | ✅ |
| `lives` | `int` | Remaining lives (default: 3) | ✅ |
| `shield_active` | `bool` | Invulnerability status | ✅ |
| `mega_shot_active` | `bool` | Piercing shot status | ✅ |

| Method | Return Type | Parameters | Description |
|:---|:---|:---|:---|
| `move(dx, dy)` | `None` | `dx: float, dy: float` | Apply delta with clamping. Diagonal normalized by ×0.707. |
| `update(keys)` | `None` | `keys: dict` | Called every frame. Reads pygame key states (WASD/arrows). |
| `move_toward(target_x, target_y)` | `None` | `target_x: int, target_y: int` | Touch control: ship follows finger, stops when distance < 4 px. |
| `shoot()` | `Bullet` | — | Spawn a player bullet at ship position. |

#### 3.2.2 Enemy Class (`entities.py`)

| Attribute | Type | Description | Mandatory |
|:---|:---|:---|:---:|
| `speed` | `float` | Pixels per frame, scales with level | ✅ |
| `direction` | `int` | 1 = right, -1 = left | ✅ |
| `drop_distance` | `int` | Pixels down per wall hit (default: 20) | ✅ |
| `shoot_cooldown` | `int` | Milliseconds between shots | ✅ |
| `shoot_chance` | `float` | Probability per frame (0.0–1.0) | ✅ |

| Method | Return Type | Parameters | Description |
|:---|:---|:---|:---|
| `update()` | `None` | — | Patrol AI: move horizontally, drop on wall collision, attempt shot. |
| `shoot()` | `Bullet` | — | Spawn an enemy bullet downward. |

#### 3.2.3 APIClient Class (`api_client.py`)

| Attribute | Type | Description | Mandatory |
|:---|:---|:---|:---:|
| `_token` | `str` | JWT access token | ✅ |
| `_player_id` | `int \| None` | Extracted from JWT payload | ✅ |
| `_username` | `str \| None` | Extracted from JWT payload | ✅ |
| `_session_id` | `int \| None` | Current game session ID | ❌ (set after `create_session`) |

| Method | Return Type | Parameters | Description |
|:---|:---|:---|:---|
| `set_token(token)` | `None` | `token: str` | Decode JWT payload, set `_player_id` / `_username`. |
| `is_authenticated()` | `bool` | — | Check if a token is present (guest = no token). |
| `create_session(world_id)` | `dict \| None` | `world_id: int \| None` | POST `/api/game/sessions`. Returns `{id, world_id, started_at}`. |
| `submit_leaderboard(score, world_id, level_id, character_used, duration_sec, accuracy_pct, enemies_killed, powerups_used, bullets_fired, replay_hash)` | `dict \| None` | run stats + anti-cheat `replay_hash` | **The real score path.** Desktop → `POST /api/game/leaderboard/submit`; browser → JS bridge `SI3LN_submit_score(json)`. |
| `submit_progress(unlocked_worlds, world_levels)` | `dict \| None` | `unlocked_worlds: list, world_levels: dict` | Persist progression. Desktop → `PATCH /api/game/progress`; browser → bridge `SI3LN_save_progress`. |
| `get_progress()` | `dict \| None` | — | Read progression. Desktop → `GET /progress`; browser → reads `SI3LN_PROGRESS_CACHE`. |
| `get_leaderboard_global(world, limit)` | `list` | `world: int \| None, limit: int` | Desktop → `GET /leaderboard/global`; browser → reads `SI3LN_LEADERBOARD_CACHE` (pre-fetched by the host page). |
| `get_leaderboard_player(player_id)` | `dict \| None` | `player_id: int \| None` | `GET /leaderboard/player/{id}` — personal bests + recent runs. |
| `_post/_get/_patch(endpoint, payload)` | `dict \| None` | `endpoint: str, payload: dict` | Internal: HTTP with Bearer JWT, 5s timeout (**desktop only** — no-op in WASM). |

> **⚠️ Browser vs desktop:** In the Pygbag/WASM build, direct HTTP is impossible (sandbox). All API calls are **delegated to JavaScript bridges** on the host page (`web_dashboard/game/index.html`), which perform the real `fetch` with the JWT. See §5.5.

#### 3.2.4 AuthSystem Class (`auth.py`)

| Attribute | Type | Description | Mandatory |
|:---|:---|:---|:---:|
| `current_user` | `dict \| None` | Logged-in user data | ❌ |
| `users_file` | `str` | Path to local JSON storage (`data/users.json`) | ✅ |

| Method | Return Type | Parameters | Description |
|:---|:---|:---|:---|
| `register(username, password)` | `bool` | `username: str, password: str` | Validate uniqueness, hash password, save to JSON. |
| `login(username, password)` | `bool` | `username: str, password: str` | Check credentials against local JSON. |
| `login_as_guest()` | `None` | — | Set current_user to guest (no persistence). |
| `logout()` | `None` | — | Clear current_user and token. |
| `update_user_data()` | `None` | — | Flush current state to local JSON. |

#### 3.2.5 ScoreManager Class (`scores.py`)

| Attribute | Type | Description | Mandatory |
|:---|:---|:---|:---:|
| `scores` | `list[dict]` | In-memory top-20 leaderboard | ✅ |
| `scores_file` | `str` | Path to local JSON storage (`data/scores.json`) | ✅ |

| Method | Return Type | Parameters | Description |
|:---|:---|:---|:---|
| `add_score(score)` | `int` | `score: int` | Insert, sort descending, keep top 20, save to JSON. Returns rank. |
| `get_top_scores(n)` | `list[dict]` | `n: int` | Return top N entries as `{rank, score, date}`. |
| `is_high_score(score)` | `bool` | `score: int` | Check if score exceeds the 20th-place threshold. |
| `get_rank(score)` | `int` | `score: int` | Compute hypothetical rank without inserting. |

### 3.3 Database Schema — Backend (PostgreSQL via Django ORM)

> **Note:** The database schema was designed by Melissa Sbibih (backend lead). It is included here to provide full-system context for the game client's API integration.

```mermaid
erDiagram
    User ||--|| Player : "has_profile"
    Player ||--o{ GameSession : "plays"
    Player ||--o{ LeaderboardEntry : "submits"
    Player ||--o{ ScoreSubmissionLog : "rate_limited_by"
    Player ||--o{ PlayerAchievement : "earns"
    GameSession }o--|| World : "played_in"
    LeaderboardEntry }o--|| World : "scored_in"
    PlayerAchievement }o--|| Achievement : "references"

    User {
        int id PK "NOT NULL, AUTO_INCREMENT"
        string username UK "NOT NULL, UNIQUE"
        string password "NOT NULL"
        string email "NOT NULL"
        boolean is_staff "DEFAULT FALSE"
        boolean is_superuser "DEFAULT FALSE"
        datetime date_joined "NOT NULL, DEFAULT NOW()"
    }

    Player {
        int id PK "NOT NULL, AUTO_INCREMENT"
        int user_id FK "NOT NULL → User.id"
        string username UK "NOT NULL, UNIQUE"
        int total_score "DEFAULT 0"
        int games_played "DEFAULT 0"
        int highest_level "DEFAULT 0"
        string avatar "NULLABLE"
        string bio "NULLABLE"
        string bg_color "NULLABLE"
        boolean show_scores "DEFAULT TRUE"
        json progression "unlocked_worlds[] + world_levels{} (JSONField)"
        datetime created_at "NOT NULL, DEFAULT NOW()"
    }

    GameSession {
        int id PK "NOT NULL, AUTO_INCREMENT"
        int player_id FK "NULLABLE → Player.id (guest = NULL)"
        int world_id FK "NOT NULL → World.id"
        int score "DEFAULT 0"
        int level_reached "DEFAULT 0"
        boolean completed "DEFAULT FALSE"
        datetime started_at "NOT NULL, DEFAULT NOW()"
        datetime ended_at "NULLABLE"
    }

    LeaderboardEntry {
        uuid id PK "NOT NULL, DEFAULT uuid4()"
        int player_id FK "NOT NULL → Player.id"
        string player_name "denormalized, indexed"
        int score "DEFAULT 0, indexed"
        int game_world_id "0=BootCamp … 5=Apocalyptic"
        int level_id "DEFAULT 1"
        string character_used ""
        int duration_sec "DEFAULT 0"
        decimal accuracy_pct "0–100"
        int enemies_killed "DEFAULT 0"
        string replay_hash "anti-cheat input hash"
        boolean verified "DEFAULT FALSE"
        boolean flagged "DEFAULT FALSE"
        boolean is_pb "personal best"
        datetime created_at "NOT NULL, DEFAULT NOW()"
    }

    ScoreSubmissionLog {
        int id PK "NOT NULL, AUTO_INCREMENT"
        int player_id FK "NOT NULL → Player.id"
        string ip_hash "hashed IP for rate-limit"
        int score "DEFAULT 0"
        boolean accepted "DEFAULT TRUE"
        string rejection_reason ""
        datetime submitted_at "NOT NULL, DEFAULT NOW()"
    }

    World {
        int id PK "NOT NULL, AUTO_INCREMENT"
        string name UK "NOT NULL, UNIQUE"
        string description "NOT NULL"
        string bullet_color "NOT NULL"
        int enemy_count "DEFAULT 10"
        string background_image "NOT NULL"
    }

    Achievement {
        int id PK "NOT NULL, AUTO_INCREMENT"
        string name UK "NOT NULL, UNIQUE"
        string description "NOT NULL"
        int points "DEFAULT 0"
        string rarity "DEFAULT 'common'"
        string requirement "NOT NULL"
    }

    PlayerAchievement {
        int id PK "NOT NULL, AUTO_INCREMENT"
        int player_id FK "NOT NULL → Player.id"
        int achievement_id FK "NOT NULL → Achievement.id"
        datetime earned_at "NOT NULL, DEFAULT NOW()"
    }
```

**Key Relationships:**
- **User → Player:** One-to-One. Each Django auth user has exactly one game player profile.
- **Player → GameSession:** One-to-Many. A player may have multiple game sessions over time.
- **Player → PlayerAchievement:** One-to-Many. A player may earn multiple achievements.
- **GameSession → World:** Many-to-One. Each session is played in exactly one world.
- **PlayerAchievement → Achievement:** Many-to-One. Each earned instance references one achievement definition.
- **Player → LeaderboardEntry:** One-to-Many. **This is the real scoreboard.** Each completed run is one immutable entry (UUID PK) with full stats and anti-cheat fields (`replay_hash`, `verified`, `flagged`). The global leaderboard reads **verified entries only**.
- **Player → ScoreSubmissionLog:** One-to-Many. Every submission attempt is logged (accepted or rejected) to enforce **rate limiting** (1 submission / 10 s).
- **Player.progression (JSONField):** Stores `{unlocked_worlds: [...], world_levels: {...}}`, merged **monotonically** server-side (a level max never decreases).
- **Guest Play:** `GameSession.player_id` is nullable; guests generate no `LeaderboardEntry` (no token → nothing submitted).

> **⚠️ Two distinct score paths — do not confuse them:** `GameSession` tracks the *lifecycle* of a play session (start/end). `LeaderboardEntry` is the *authoritative score record* shown on the leaderboard and in the profile's best scores. Real scores are submitted via `POST /leaderboard/submit`, **not** via the session PATCH.

### 3.4 UML Class Diagram — Complete Game Client

```mermaid
classDiagram
    class Game {
        +state: str
        +screen: Surface
        +running: bool
        +handle_events()
        +update()
        +draw()
        +start_gameplay()
        +end_game()
        +run()
    }

    class Player {
        +speed: int
        +rect: Rect
        +lives: int
        +shield_active: bool
        +mega_shot_active: bool
        +move(dx, dy)
        +update(keys)
        +move_toward(x, y)
        +shoot() Bullet
    }

    class Enemy {
        +speed: float
        +direction: int
        +drop_distance: int
        +shoot_cooldown: int
        +shoot_chance: float
        +update()
        +shoot() Bullet
    }

    class Bullet {
        +velocity: int
        +is_enemy: bool
        +update()
    }

    class Explosion {
        +frame_index: int
        +max_frames: int
        +update()
    }

    class Bonus {
        +type: str
        +duration: int
        +update()
    }

    class SpecialAttack {
        +damage: int
        +aoe_radius: int
        +update()
    }

    class AuthSystem {
        +current_user: dict
        +users_file: str
        +register(username, password) bool
        +login(username, password) bool
        +login_as_guest()
        +logout()
        +update_user_data()
    }

    class ScoreManager {
        +scores: list
        +scores_file: str
        +add_score(score) int
        +get_top_scores(n) list
        +is_high_score(score) bool
        +get_rank(score) int
    }

    class APIClient {
        +_token: str
        +_player_id: int
        +_username: str
        +_session_id: int
        +set_token(token)
        +is_authenticated() bool
        +create_session(world_id) dict
        +submit_leaderboard(score, world_id, level_id, replay_hash, ...) dict
        +submit_progress(unlocked_worlds, world_levels) dict
        +get_progress() dict
        +get_leaderboard_global(world, limit) list
        +get_leaderboard_player(player_id) dict
    }

    class ResolutionManager {
        +canvas: Surface
        +is_portrait: bool
        +screen_to_ref(x, y) tuple
        +present(screen)
    }

    class LevelSelector {
        +worlds: list
        +selected_world: int
        +draw()
        +handle_event(event)
        +is_level_unlocked(level) bool
    }

    class ProfileScreen {
        +stats: dict
        +draw()
        +handle_event(event)
        +refresh_stats()
    }

    class Button {
        +rect: Rect
        +text: str
        +hover: bool
        +draw()
        +handle_event(event) bool
    }

    class InputField {
        +rect: Rect
        +text: str
        +is_password: bool
        +focused: bool
        +draw()
        +handle_event(event)
    }

    Game --> Player : "spawns"
    Game --> Enemy : "spawns"
    Game --> Bullet : "spawns"
    Game --> Explosion : "spawns"
    Game --> Bonus : "spawns"
    Game --> SpecialAttack : "spawns"
    Game --> AuthSystem : "uses"
    Game --> ScoreManager : "uses"
    Game --> APIClient : "uses"
    Game --> ResolutionManager : "uses"
    Game --> LevelSelector : "uses"
    Game --> ProfileScreen : "uses"
    Player --> Bullet : "shoots"
    Enemy --> Bullet : "shoots"
    LevelSelector --> ProfileScreen : "navigates"
    ProfileScreen --> AuthSystem : "reads"
```

---

## 4. High-Level Sequence Diagrams

The following sequence diagrams illustrate the primary interactions between the player, game client, API, and database for key use cases.

### 4.1 Game Session — Full Playthrough

```mermaid
sequenceDiagram
    autonumber
    participant Player as Player
    participant GameClient as Game Client
    participant Entities as Entities
    participant APIClient as API Client
    participant DjangoAPI as Django API
    participant PostgreSQL as PostgreSQL

    Player->>GameClient: Click "PLAY"
    GameClient->>GameClient: state = PLAYER_SELECT
    GameClient->>Entities: select character sprite
    GameClient->>GameClient: state = LEVEL_SELECT
    GameClient->>GameClient: select "Space World"
    GameClient->>APIClient: create_session(world_id=1)
    APIClient->>DjangoAPI: POST /api/game/sessions
    DjangoAPI->>PostgreSQL: INSERT INTO GameSession
    PostgreSQL-->>DjangoAPI: RETURNING id
    DjangoAPI-->>APIClient: { session_id, world_id }
    APIClient-->>GameClient: _session_id set
    GameClient->>Entities: spawn Player + Enemy wave

    loop Gameplay Loop (60 FPS)
        Player->>GameClient: Press keys / Touch drag
        GameClient->>Entities: update()
        Entities->>Entities: move / shoot
        GameClient->>GameClient: check_collisions()
        GameClient->>Entities: bullet-enemy collision
        Entities-->>GameClient: explosion + score increment
        GameClient->>Entities: enemy-player collision
        Entities-->>GameClient: lives decrement
    end

    GameClient->>GameClient: lives == 0
    GameClient->>GameClient: end_game() → build payload + replay_hash
    GameClient->>APIClient: submit_leaderboard(score, world_id, level_id, replay_hash, ...)
    APIClient->>DjangoAPI: POST /api/game/leaderboard/submit
    DjangoAPI->>DjangoAPI: anti-cheat (rate limit + max-score + replay_hash)
    DjangoAPI->>PostgreSQL: INSERT LeaderboardEntry (verified/flagged)
    PostgreSQL-->>DjangoAPI: entry_id
    DjangoAPI-->>APIClient: { success, is_pb, new_rank }
    APIClient-->>GameClient: score saved
    GameClient-->>Player: Display Game Over + Rank
```

**Key Interaction:** The game client initiates a tracked session via the API before gameplay begins, ensuring every score submission is associated with a valid session record. This prevents orphaned score data.

### 4.2 In-Game Authentication Flow

```mermaid
sequenceDiagram
    autonumber
    participant Player as Player
    participant GameClient as Game Client
    participant AuthSystem as AuthSystem (Local)
    participant APIClient as API Client
    participant DjangoAPI as Django API
    participant PostgreSQL as PostgreSQL

    Player->>GameClient: Click "CONNEXION"
    GameClient->>GameClient: state = LOGIN
    Player->>GameClient: Enter username + password
    GameClient->>AuthSystem: login(username, password)
    AuthSystem->>AuthSystem: read local users.json

    alt Local user exists
        AuthSystem-->>GameClient: success, current_user set
        GameClient-->>Player: Display "Welcome {username}!"
    else Local user not found
        GameClient->>APIClient: POST /api/auth/login
        APIClient->>DjangoAPI: validate credentials
        DjangoAPI->>PostgreSQL: SELECT * FROM User WHERE username=...
        PostgreSQL-->>DjangoAPI: user record
        DjangoAPI-->>APIClient: return JWT token
        APIClient->>APIClient: decode JWT payload
        APIClient-->>GameClient: player_id, username
        GameClient->>AuthSystem: save to local users.json
        AuthSystem-->>GameClient: auto-login next boot
        GameClient-->>Player: Display "Welcome {username}!"
    end
```

**Key Interaction:** The dual-auth strategy (local JSON + server JWT) ensures the player can authenticate even when offline. Upon first successful server login, credentials are mirrored locally for subsequent offline sessions.

### 4.3 Score Submission to the Leaderboard (with Anti-Cheat)

This is the **real** score path: on a completed run, the game submits to the persistent leaderboard through `POST /api/game/leaderboard/submit`. In the browser build the request is relayed by a **JavaScript bridge** because WASM cannot make direct HTTP calls.

```mermaid
sequenceDiagram
    autonumber
    participant GameClient as Game Client (WASM)
    participant Bridge as JS Bridge (game/index.html)
    participant DjangoAPI as Django API
    participant PostgreSQL as PostgreSQL

    GameClient->>GameClient: end_game() → build payload + SHA-256 replay_hash
    GameClient->>Bridge: platform.window.SI3LN_submit_score(json)
    Bridge->>Bridge: read JWT from localStorage
    Bridge->>DjangoAPI: POST /api/game/leaderboard/submit (Bearer JWT)
    Note over Bridge,DjangoAPI: { score, world_id, level_id, replay_hash, enemies_killed, ... }

    DjangoAPI->>DjangoAPI: 1. rate limit (1 / 10s per player+IP)
    DjangoAPI->>DjangoAPI: 2. validate max possible score (server-side)
    DjangoAPI->>DjangoAPI: 3. verify replay_hash (len ≥ 16)
    DjangoAPI->>PostgreSQL: INSERT LeaderboardEntry (verified / flagged)
    DjangoAPI->>PostgreSQL: INSERT ScoreSubmissionLog (accepted/rejected)
    PostgreSQL-->>DjangoAPI: entry_id
    DjangoAPI-->>Bridge: { success, entry_id, is_pb, new_rank, flagged }
    Bridge->>Bridge: SI3LN_fetch_leaderboard() → refresh cache
```

**Key Interaction:** Every submission is stored **immutably** as a new `LeaderboardEntry` and passes a 3-layer anti-cheat gate. If the `replay_hash` is missing/invalid the entry is written but **flagged & unverified**, so it never appears on the global leaderboard (which filters `verified = true`). Only authenticated runs are submitted — a guest has no token, so the bridge sends nothing.

### 4.4 Web Dashboard → Game Client Flow

```mermaid
sequenceDiagram
    autonumber
    participant Player as Player
    participant Dashboard as Web Dashboard (Vanilla JS)
    participant Wrapper as game/index.html (JS bridges)
    participant GameClient as Pygbag Game (WASM)
    participant DjangoAPI as Django API

    Player->>Dashboard: Click "Play Now"
    Dashboard->>Dashboard: JWT already in localStorage (SI3LN_SESSION)
    Dashboard->>Wrapper: load iframe /game/ (same origin)
    Wrapper->>Wrapper: read JWT from localStorage → window.SI3LN_JWT_TOKEN
    Wrapper->>DjangoAPI: pre-fetch GET /leaderboard/global → SI3LN_LEADERBOARD_CACHE
    Wrapper->>DjangoAPI: pre-fetch GET /progress → SI3LN_PROGRESS_CACHE
    Wrapper->>GameClient: load /pygbag/ iframe (inherits localStorage)
    GameClient->>GameClient: reads platform.window.SI3LN_JWT_TOKEN → is_authenticated

    loop Gameplay Loop (local, 0 network)
        Player->>GameClient: Play level
    end

    GameClient->>Wrapper: SI3LN_submit_score(json)
    Wrapper->>DjangoAPI: POST /leaderboard/submit (Bearer JWT)
    DjangoAPI-->>Wrapper: { success, new_rank }
    Wrapper->>Wrapper: refresh SI3LN_LEADERBOARD_CACHE
```

**Key Interaction:** The token is **never passed via URL params**. Because the dashboard, `/game/`, and `/pygbag/` are all served from the **same origin**, they transparently share `localStorage` (same-origin policy) — that is how the JWT reaches the WASM game (`platform.window.SI3LN_JWT_TOKEN`). The wrapper page `game/index.html` hosts all the **JS bridges** (`SI3LN_submit_score`, leaderboard/progress caches) that stand in for the HTTP layer the sandboxed WASM cannot use.

---

## 5. External & Internal APIs

### 5.1 External APIs / Services

| Service | Purpose | Selection Justification | Auth |
|:---|:---|:---|:---|
| **Django Ninja OpenAPI** | Interactive API documentation at `/api/docs` | Automatic schema generation from Python type hints reduces documentation drift; Swagger UI enables manual testing without external tools. | None (development) |
| **Google Fonts CDN** | Arcade typography (Press Start 2P) | Consistent cross-platform font rendering; CDN delivery reduces asset bundle size; falls back to monospace if unavailable. | None |
| **Pygbag** | Pygame → WebAssembly compiler at build time | Official Pygame WASM toolchain; zero-cost browser deployment from Python source; eliminates need for JavaScript rewrite. | N/A (build tool) |

### 5.2 Internal API — Endpoints Consumed by Game Client

The game client (`api_client.py`) acts as a consumer of the Django Ninja REST API. All endpoints use JSON request/response bodies over HTTPS.

#### 5.2.1 Authentication Endpoints

| Method | Endpoint | Request Body | Response Body | HTTP Codes | Auth | Called When |
|:---|:---|:---|:---|:---|:---|:---|
| `POST` | `/api/auth/register` | `{ "username": str, "email": str, "password": str }` | `{ "token": str, "username": str, "player_id": int }` | 201, 400, 409 | Public | Player creates account in-game |
| `POST` | `/api/auth/login` | `{ "username": str, "password": str }` | `{ "token": str, "username": str, "player_id": int }` | 200, 401 | Public | Player logs in |
| `POST` | `/api/auth/logout` | — | `{ "success": bool }` | 200, 401 | Bearer | Player logs out |
| `GET` | `/api/auth/me` | — | `{ "username": str, "player_id": int, "email": str }` | 200, 401 | Bearer | Verify active session on boot |

**Example Request/Response — Login:**

```http
POST /api/auth/login HTTP/1.1
Host: api.arcad3x.example.com
Content-Type: application/json

{
  "username": "hugoramos",
  "password": "securepassword123"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "hugoramos",
  "player_id": 42
}
```

#### 5.2.2 Game Session Endpoints

| Method | Endpoint | Request Body | Response Body | HTTP Codes | Auth | Called When |
|:---|:---|:---|:---|:---|:---|:---|
| `POST` | `/api/game/sessions` | `{ "world_id": int \| null }` | `{ "id": int, "world_id": int, "started_at": datetime }` | 201, 400, 401 | Bearer | Gameplay starts (session *lifecycle* only) |
| `PATCH` | `/api/game/sessions/{id}` | `{ "score": int, "level_reached": int, "completed": bool }` | `{ "id": int, "score": int, "ended_at": datetime }` | 200, 400, 401, 404 | Bearer | Marks a session ended (⚠️ **not** the leaderboard score path) |
| `GET` | `/api/game/worlds` | — | `[{ "id": int, "name": str, "description": str }]` | 200 | Public | Level selector populates worlds |
| `GET` | `/api/game/profile/me` | — | `{ "username": str, "total_score": int, "games_played": int, "highest_level": int }` | 200, 401 | Bearer | Profile screen stats |

#### 5.2.3 Leaderboard v2 & Progression Endpoints *(the real scoreboard)*

| Method | Endpoint | Request / Query | Response Body | Auth | Called When |
|:---|:---|:---|:---|:---|:---|
| `POST` | `/api/game/leaderboard/submit` | `{ score, world_id, level_id, character_used, duration_sec, accuracy_pct, enemies_killed, bullets_fired, replay_hash }` | `{ success, entry_id, is_pb, new_rank, flagged }` | Bearer | **On run completion — the actual score submission** |
| `GET` | `/api/game/leaderboard/global` | `?world=&limit=` | `{ "entries": [{ player_name, score, world_id, level_id, verified, ... }] }` | Public | Leaderboard page / in-game (via cache) |
| `GET` | `/api/game/leaderboard/player/{id}` | — | `{ personal_bests: [...], recent_runs: [...], best_score, total_runs }` | Public | Profile "best scores" |
| `GET` | `/api/game/leaderboard/nearby` | `?player=&radius=` | `{ entries: [...] }` | Public | Rank context around a player |
| `GET` | `/api/game/progress` | — | `{ unlocked_worlds: [str], world_levels: { "0": int, ... } }` | Bearer | Restore progression on boot |
| `PATCH` | `/api/game/progress` | `{ unlocked_worlds: [str], world_levels: {} }` | merged progression | Bearer | After each level won (monotonic merge) |
| `POST` | `/api/auth/refresh` | — (Bearer) | `{ token, username, player_id }` | Bearer | Token rotation (old token blacklisted) |

**Example Request/Response — Create Session:**

```http
POST /api/game/sessions HTTP/1.1
Host: api.arcad3x.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "world_id": 1
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 157,
  "world_id": 1,
  "started_at": "2025-05-27T14:32:00Z"
}
```

**Example Request/Response — Submit Score to Leaderboard:**

```http
POST /api/game/leaderboard/submit HTTP/1.1
Host: api.arcad3x.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "score": 12450,
  "world_id": 1,
  "level_id": 3,
  "character_used": "Star Fighter",
  "duration_sec": 62,
  "accuracy_pct": 91.5,
  "enemies_killed": 48,
  "bullets_fired": 53,
  "replay_hash": "415d736af2c488dab8e3de4adec68d15"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "entry_id": "347e7a9a-a38d-4691-ab06-f5cc33040b4c",
  "is_pb": true,
  "new_rank": 1,
  "flagged": false,
  "message": "Score submitted successfully."
}
```

> A submission with a missing/short `replay_hash` returns `"flagged": true` and the entry is **hidden** from the global leaderboard until verified.

### 5.3 JWT Token Specification

| Attribute | Value | Justification |
|:---|:---|:---|
| **Algorithm** | HS256 (HMAC-SHA256) | Industry standard for signed JWTs; sufficient security for academic/MVP scope without public-key infrastructure complexity. |
| **Secret** | `JWT_SECRET_KEY` (signature) + `JWT_PEPPER` (2nd secret) | **Dual-secret / secret separation.** The token is signed with `JWT_SECRET_KEY`; a `peppered_id = HMAC-SHA256(JWT_PEPPER, user_id)` claim is embedded and re-checked on every request. If the signing key leaks, an attacker still needs the pepper to forge a valid token. |
| **Access Token Expiry** | 24 hours | Balances security (short-lived) with usability (no re-login during a play session). |
| **Payload Claims** | `{ user_id, username, player_id, peppered_id, is_staff, is_superuser, iat, exp, jti, type: "access" }` | `player_id` avoids a DB lookup per request; `jti` (UUID) makes every token unique; `peppered_id` is the 2nd-secret check; `is_staff`/`is_superuser` are role hints for the frontend. |
| **Revocation** | **Redis blacklist** (`bl:<token>`, TTL 48h) | JWT is *stateless* — to support **logout** and **token rotation** (refresh), the invalidated token is added to a Redis blacklist checked on every request. Shared across all Gunicorn workers; falls back to an in-memory set if Redis is down. |
| **Header Format** | `Authorization: Bearer <token>` | RFC 6750 standard. |
| **Client Storage** | `localStorage` (`SI3LN_SESSION`) in browser / env var (desktop) | Browser: shared with the game iframe via same-origin policy → `platform.window.SI3LN_JWT_TOKEN`. |

### 5.4 Game ↔ API Data Flow

```
┌─────────────┐   POST /sessions {world_id}   ┌─────────────┐
│   Game      │ ────────────────────────────▶ │  Django API │
│  Client     │ ◀──────────────────────────── │   /game/    │
│             │        { session_id }          └─────────────┘
│  GAMEPLAY   │                                       │ ORM
│  (local,    │                                       ▼
│   0 net)    │   POST /leaderboard/submit      ┌─────────────┐
│             │   {score, replay_hash, ...}     │  PostgreSQL │
│             │ ────────────────────────────▶   │ Leaderboard │
│             │      [anti-cheat gate]          │   Entry     │
│             │ ◀──────────────────────────── │  (+ Log)    │
│             │   {success, new_rank, flagged} └─────────────┘
└─────────────┘   (browser: via SI3LN_submit_score JS bridge)
```

**Flow Description:**
1. **Session Initiation:** The client POSTs to `/api/game/sessions` with an optional `world_id` when a level starts — this records the session *lifecycle* only.
2. **Local Gameplay:** All gameplay (movement, shooting, collisions, scoring) runs locally in the Pygame loop. **No API calls during active gameplay** → zero latency.
3. **Score Submission:** On run completion, the client submits the final stats + `replay_hash` to **`POST /api/game/leaderboard/submit`** (in the browser, relayed by the `SI3LN_submit_score` JS bridge). The server runs anti-cheat (rate limit → max-score validation → replay-hash check) and inserts an immutable `LeaderboardEntry` (`verified` or `flagged`).
4. **Progression:** After each level won, the client PATCHes `/api/game/progress`; the server **merges monotonically** (a level max never decreases).
5. **Leaderboard Refresh:** The client re-reads `/api/game/leaderboard/global` (browser: from the pre-fetched `SI3LN_LEADERBOARD_CACHE`) to show updated rankings — global leaderboard returns **verified entries only**.

### 5.5 Anti-Cheat & Score Integrity

Because scores are submitted by a client the server does not control, `/leaderboard/submit` enforces a **defense-in-depth** gate before an entry becomes visible:

| Layer | Mechanism | Effect |
|:---|:---|:---|
| 1. **Authentication** | JWT required (`auth=jwt_auth`) | Guests cannot submit — no token, no entry. |
| 2. **Rate limiting** | 1 submission / 10 s per player + IP hash (`ScoreSubmissionLog`) | Blocks flooding / scripted spam. |
| 3. **Server-side score cap** | `_validate_max_possible_score(score, enemies_killed, level_id, powerups, bullets)` | Rejects physically impossible scores (e.g. 9 999 999). |
| 4. **Replay-hash check** | `replay_hash` must be present and ≥ 16 chars (SHA-256 of run stats) | Missing/invalid → entry stored but `verified=false, flagged=true`. |
| 5. **Verified-only display** | `/leaderboard/global` filters `verified = true` | Flagged runs never appear on the public board. |

> **Honest limitation (worth stating at defense):** the server does **not** yet fully re-simulate the run from inputs — it validates the hash is well-formed and flags suspicious runs for review. This is an MVP-level, extensible anti-cheat, not a cryptographic guarantee.

### 5.6 Browser Bridge Architecture (WASM ↔ JS ↔ API)

In the desktop build, `api_client.py` calls the API directly with `requests`. In the **browser build this is impossible** — the Pygbag/WASM runtime is sandboxed and has no socket access. The game therefore delegates every network operation to **JavaScript bridges** exposed on the host page (`web_dashboard/game/index.html`):

| Direction | Python call | JS bridge | Backing endpoint |
|:---|:---|:---|:---|
| Submit score | `submit_leaderboard()` | `SI3LN_submit_score(json)` | `POST /leaderboard/submit` |
| Read leaderboard | `get_leaderboard_global()` | reads `SI3LN_LEADERBOARD_CACHE` (pre-fetched) | `GET /leaderboard/global` |
| Save progression | `submit_progress()` | `SI3LN_save_progress(json)` | `PATCH /progress` |
| Read progression | `get_progress()` | reads `SI3LN_PROGRESS_CACHE` | `GET /progress` |

- **Token:** shared via **same-origin `localStorage`** → `window.SI3LN_JWT_TOKEN` → `platform.window.SI3LN_JWT_TOKEN` (read by Python).
- **Reads are cached:** the host page pre-fetches the leaderboard/progression into JS globals so the game can read them synchronously mid-loop, with no `await` and no latency. The leaderboard cache is refreshed after each submit.

---

## 6. SCM & QA Plans

### 6.1 Source Control Management (SCM) Plan

#### 6.1.1 Platform & Repository Structure

| Aspect | Strategy | Justification |
|:---|:---|:---|
| **Platform** | GitHub (`Schpser/SI3LN_Python`) | Academic standard; public visibility for portfolio; free CI/CD via GitHub Actions. |
| **Repository Type** | Monorepo | Single source of truth. Contains `Game_Python/` (game), `api/` (Django/Ninja, project `si3ln_api`), `web_dashboard/` (JS SPA), `mobile/`, `Tests/`, and `Docker/docker-compose.yml` (db · redis · api · frontend). |
| **Commit Convention** | Conventional Commits | `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:` prefixes enable automated changelog generation. |

#### 6.1.2 Branching Strategy

```mermaid
graph LR
    subgraph Mainline["Mainline"]
        M[main<br/>stable release]
    end
    subgraph Features["Feature Branches"]
        F1[feature/player-select]
        F2[feature/api-integration]
        F3[feature/mobile-controls]
    end
    subgraph Hotfix["Hotfix"]
        H[hotfix/score-double-count]
    end

    F1 -->|Pull Request| M
    F2 -->|Pull Request| M
    F3 -->|Pull Request| M
    H -->|Emergency PR| M

    style M fill:#66bb6a,stroke:#fff,stroke-width:2px
    style F1 fill:#4fc3f7,stroke:#fff
    style F2 fill:#4fc3f7,stroke:#fff
    style F3 fill:#4fc3f7,stroke:#fff
    style H fill:#ef5350,stroke:#fff
```

**Branch Rules:**
- `main`: Always deployable. Protected branch — requires 2 approving reviews.
- `feature/*`: One branch per user story or bug fix. Created from `main`, merged via Pull Request.
- `hotfix/*`: Emergency branches for critical bugs in production. Bypass standard review only with team consensus.

#### 6.1.3 Code Review Process

| Step | Actor | Action | SLA |
|:---|:---|:---|:---|
| 1 | Developer | Push feature branch, open PR with description linking to user story | — |
| 2 | Reviewer 1 (Hugo) | Review game client changes; verify no Pygame anti-patterns | ≤ 24h |
| 3 | Reviewer 2 (Melissa) | Review API contract changes; verify no breaking schema changes | ≤ 24h |
| 4 | CI Bot | Run `pytest` suite; block merge on test failure | Automatic |
| 5 | Developer | Address review comments, push fixes | — |
| 6 | Both Reviewers | Re-review, approve | ≤ 12h |
| 7 | Developer | Squash-merge to `main` | — |

#### 6.1.4 Definition of Done (DoD)

A feature or fix is considered complete when **all** of the following criteria are satisfied:

- [ ] Code compiles/executes without errors in the target environment (Python 3.10+ / Pygame 2.5+).
- [ ] Unit tests added or updated for all new logic (minimum 80% branch coverage for game math).
- [ ] Integration tests pass for all modified API endpoints.
- [ ] Manual playtesting completed on both keyboard and touch controls.
- [ ] Code reviewed and approved by at least one team member.
- [ ] Documentation updated (README, inline comments, or this Stage 3 document).
- [ ] No secrets or credentials committed to the repository (verified via `git-secrets` scan).
- [ ] Asset files (PNG, WAV, TTF) are optimized and do not exceed 2MB individually.

### 6.2 Quality Assurance (QA) Plan

#### 6.2.1 Testing Pyramid

| Layer | Tool / Method | Scope | Functional Requirement | Frequency |
|:---|:---|:---|:---|:---|
| **Unit Tests** | `pytest` + `test_game_units.py` | Entity math, boundary clamping, diagonal normalization (×0.707), collision rectangles | US-M3, US-M4 | Every commit |
| **Integration Tests** | `pytest` + `Tests/test_api_full.py` | `api_client.py` against mocked Django API; JWT injection, timeout handling, JSON parsing | US-M5 | Every PR |
| **Security Tests** | `pytest` + `Tests/test_security.py` | Token expiry, SQL injection resistance, rate limiting compliance | NFR-Security | Weekly |
| **Manual QA** | Physical playtesting | Keyboard (WASD/arrows + space) + touch (drag-to-move, auto-fire, on-screen buttons) on desktop and mobile | US-S3 | Before each release |
| **Performance QA** | `time.perf_counter` in `game.py` | Maintain 60 FPS at 1280×720 with 15 enemies + 20 bullets + particle effects | NFR-Performance | Before each release |
| **Asset QA** | Visual inspection | 5 world backgrounds, 7+ character sprites, enemy/boss sprite sheets load without distortion | US-S1, US-S2 | Before each release |
| **Responsive QA** | Window resize torture test | Landscape → portrait → fullscreen → windowed; all UI buttons remain clickable | NFR-Usability | Before each release |

#### 6.2.2 Test Case Example — Diagonal Movement (BUG-001)

| ID | Input | Expected Output | Actual Output (Pre-Fix) | Actual Output (Post-Fix) |
|:---|:---|:---|:---|:---|
| BUG-001-T1 | `dx=1, dy=1` | `speed = 8 × 0.707 ≈ 5.66 px/frame` | `speed = 8 + 8 = 16 px/frame` (too fast) | `speed = 5.66 px/frame` (correct) |
| BUG-001-T2 | `dx=1, dy=0` | `speed = 8 px/frame` | `speed = 8 px/frame` | `speed = 8 px/frame` (unchanged) |

**Fix:** In `entities.py`, the `Player.update()` method now checks `if dx and dy:` and multiplies both components by `0.70710678118` (1/√2) before calling `move()`.

#### 6.2.3 Bug Management Process

| Phase | Action | Owner | Tool |
|:---|:---|:---|:---|
| **Discovery** | Report via GitHub Issues with reproduction steps, expected vs. actual behavior, and environment details | Anyone | GitHub Issues |
| **Triage** | Label as `bug`, assign priority (P0 = crash/blocker, P1 = functional, P2 = cosmetic) | Team Lead | GitHub Labels |
| **Reproduction** | Create minimal reproduction script or test case | Developer | pytest |
| **Fix** | Develop fix on `feature/fix-XXX` branch | Developer | Git + IDE |
| **Verification** | Run reproduction test; verify fix + no regressions | Reviewer | pytest + manual |
| **Release** | Merge to `main`, tag release, update changelog | Developer | GitHub Releases |

#### 6.2.4 Known Bugs Fixed (Game Client)

| Bug ID | Description | Fix | File | Functional Requirement |
|:---|:---|:---|:---|:---|
| BUG-001 | Diagonal movement speed exceeds intended maximum (vector sum > 1) | Multiply `dx` and `dy` by `0.70710678118` when both non-zero | `entities.py` | US-M3 |
| BUG-002 | Player statistics double-counted on replay (score submitted twice) | Add `was_completed` idempotency check before API PATCH | `game.py` | US-M5 |
| BUG-003 | Touch controls jitter when finger position is close to ship center | Add early exit `if dist < 4: return` in `move_toward()` | `entities.py` | US-S3 |

---

## 7. Technical Justifications

### 7.1 Technology Choices — Game Client

| Technology | Functional Requirement | Non-Functional Requirement | Selection Justification | Trade-off |
|:---|:---|:---|:---|:---|
| **Python / Pygame** | US-M3 (2D arcade gameplay) | NFR-Performance (60 FPS) | Rapid 2D prototyping; mature sprite/collision ecosystem (`pygame.sprite.Group`); same language as backend reduces team cognitive load; Pygbag compiles to WASM for browser. | GIL limits true parallelism; 60 FPS cap acceptable for 2D arcade scope; not suitable for 3D or heavy physics. |
| **Pygbag (WebAssembly)** | US-M3 (browser play) | NFR-Usability (zero-install) | Official Pygame WASM toolchain; zero-install browser play — players visit a URL and play immediately. Critical for accessibility and academic demo. | WASM bundle ~10MB initial load; slower startup than native `.exe`; acceptable for MVP. |
| **Local JSON Storage** | US-M1 (offline play) | NFR-Reliability (graceful degradation) | `AuthSystem` stores users in `data/users.json`; `ScoreManager` keeps top-20 in `data/scores.json`. Enables offline play with instant feedback. | Not shared across devices; server sync via `api_client.py` fills this gap. |
| **ResolutionManager** | US-S3 (cross-platform) | NFR-Usability (responsive) | Fixed 1280×720 reference canvas scaled to any window. One codebase supports desktop (landscape) and mobile (portrait) without coordinate rewriting. | Letterboxing on ultra-wide screens; minor visual compromise acceptable. |
| **Touch Controls (Mouse Events)** | US-S3 (mobile play) | NFR-Usability (accessibility) | Mouse events (`MOUSEBUTTONDOWN`, `MOUSEMOTION`) mapped to touch via Pygbag. Drag-to-move + on-screen fire/shield/mega buttons. | Less precise than keyboard for competitive play; suitable for casual mobile use. |

### 7.2 Architecture Decisions

| Decision | Context | Functional Requirement | Non-Functional Requirement | Rationale |
|:---|:---|:---|:---|:---|
| **State Machine over Scene Graph** | Arcade games have discrete screens (menu → select → play → over) | US-M1, US-M2 | Maintainability | String-based state + per-state `update()`/`draw()` branches are simpler than a full scene graph for a team of 2. Reduces boilerplate and learning curve. |
| **Sprite Groups for Collision** | 15 enemies + 20 bullets + player + explosions simultaneously | US-M3 | NFR-Performance | Pygame's `pygame.sprite.Group` + `spritecollide()` / `groupcollide()` provide built-in collision detection with dirty-rect optimization. No custom spatial hash needed at this entity count. |
| **Dual Auth (local + JWT)** | Players may have intermittent connectivity | US-M1, US-M2 | NFR-Reliability | `AuthSystem` handles local JSON; `APIClient` handles server JWT. Offline-first: player can always play. Server acts as source of truth for global leaderboard when online. |
| **Environment-Driven API URL** | One codebase must connect to dev, staging, and production | US-M5 | Maintainability | `SI3LN_API_URL` and `SI3LN_TOKEN` environment variables enable one game binary to connect to `localhost:8000` (dev), staging, or production without recompilation. |
| **Immutable Leaderboard Entries + Anti-Cheat** | Scores come from an untrusted client and must be tamper-resistant | US-M5 | NFR-Security | Each run is an **immutable `LeaderboardEntry`** (UUID PK) rather than a mutable counter. A server-side gate (rate limit → max-score validation → `replay_hash` → `verified/flagged`) decides visibility. Immutable history also enables personal-best and audit queries. |
| **Two-Path Score Model** | Session lifecycle and the scoreboard are separate concerns | US-M4, US-M5 | Maintainability | `GameSession` records *when* a session ran; `LeaderboardEntry` records *the achieved score*. Decoupling keeps the leaderboard authoritative and independent of session bookkeeping. |

### 7.3 Constraints and Assumptions

| Constraint / Assumption | Impact | Mitigation |
|:---|:---|:---|
| Academic timeline: 4-month project | Limited scope; V2 features deferred | Explicit Won't Have list (US-W1–W3); MVP-first prioritization |
| Team size: 2 developers (1 game, 1 backend) | No dedicated QA or DevOps | Automated testing + dual review process; GitHub Actions for CI/CD |
| Target hardware: mid-range laptops and smartphones | Cannot assume GPU acceleration | Pygame software rendering; 60 FPS target on integrated graphics |
| Browser compatibility: Chrome, Firefox, Safari | WASM support varies | Pygbag targets modern browsers; provide `.exe` fallback for older systems |

---

## 8. Deployment Plan

### 8.1 Deployment Architecture

```mermaid
graph TD
    subgraph Player["Player Device"]
        Browser["Browser<br/>Chrome/Firefox/Safari"]
    end

    subgraph CDN["Static Hosting"]
        GH["GitHub Pages<br/>Free / Zero-config"]
    end

    subgraph Backend["Backend Infrastructure"]
        Render["Render<br/>Free Tier"]
        Postgres[(PostgreSQL<br/>Managed)]
    end

    Browser -->|HTTPS| GH
    Browser -->|HTTPS + CORS| Render
    Render -->|Django ORM| Postgres

    subgraph Build["Build Pipeline"]
        Pygbag["Pygbag WASM Build"]
        Actions["GitHub Actions<br/>Auto-deploy"]
    end

    Pygbag -->|Upload| GH
    Actions -->|Trigger| Render

    style Browser fill:#1a1a2e,stroke:#ffd54f
    style GH fill:#0a0a1a,stroke:#4fc3f7
    style Render fill:#0a1a0a,stroke:#66bb6a
    style Postgres fill:#1a0a1a,stroke:#ab47bc
```

### 8.2 Game Client Deployment (Pygbag WASM)

**Build Pipeline:**

```bash
# Step 1: Build WASM bundle
cd Game_Python/
python -m pygbag main.py --ume_block=0 --can_close=1

# Step 2: Output directory
# build/web/
#   ├── index.html      → Entry point
#   ├── main.py         → Transpiled Python → WASM
#   ├── main.data       → Asset bundle (sprites, fonts, sounds)
#   ├── pygbag/         → Runtime
#   └── favicon.ico

# Step 3: Deploy to static hosting
cp -r build/web/* ../docs/web/
```

**Hosting Comparison:**

| Option | Cost | Setup | Best For | Chosen |
|:---|:---|:---|:---|:---:|
| GitHub Pages | Free | Push `build/web/` to `gh-pages` branch | Academic demo, portfolio | ✅ |
| itch.io | Free | Upload ZIP of `build/web/` | Indie game showcase, beta | ❌ |
| AWS S3 + CloudFront | ~$5/month | `aws s3 sync` + CloudFront distribution | Production scale, custom domain | ❌ (V2) |
| Netlify | Free tier | Drag & drop `build/web/` folder | Quick deploy, preview URLs | ❌ |

**Decision:** GitHub Pages was selected for the MVP due to zero cost, automatic deployment via GitHub Actions, and direct integration with the academic portfolio repository.

### 8.3 Backend API Deployment

**Stack:** Django Ninja + Gunicorn + PostgreSQL + Nginx (reverse proxy)

**Docker Compose (Production):**

```yaml
# docker-compose.prod.yml
version: "3.9"
services:
  db:
    image: postgres:15-alpine
    env_file: .env
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

  api:
    build: ./api
    command: gunicorn si3ln_api.wsgi:application --bind 0.0.0.0:8000 --workers 4
    env_file: .env
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api

volumes:
  pgdata:
  redisdata:
```

**Hosting Comparison:**

| Option | Cost | Setup | Best For | Chosen |
|:---|:---|:---|:---|:---:|
| Render | Free tier | Connect GitHub repo, auto-deploy on push | MVP, quick start | ✅ |
| Railway | Free tier | Similar to Render, includes PostgreSQL | Hobby projects | ❌ |
| AWS EC2 + RDS | ~$20/month | Manual setup, full control | Production scale | ❌ (V2) |
| DigitalOcean Droplet | ~$6/month | 1-click Django, manual PostgreSQL | Full control, budget | ❌ |

**Decision:** Render was selected for the MVP due to the free tier, automatic deployment from GitHub, managed PostgreSQL, and HTTPS out of the box.

### 8.4 Environment Configuration

**`.env` (backend, never committed):**

```bash
# Database
DATABASE_URL=postgresql://user:pass@db:5432/arcad3x

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=api.arcad3x.example.com,localhost

# JWT
JWT_SECRET_KEY=another-secret-key
JWT_PEPPER=a-second-independent-secret   # 2nd secret for the peppered_id claim
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis (token blacklist / rate-limit)
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://hugou74130.github.io,https://arcad3x.itch.io

# Game Client API URL
SI3LN_API_URL=https://api.arcad3x.example.com/api
```

**Environment Separation:**

| Variable | Development | Staging | Production |
|:---|:---|:---|:---|
| `DEBUG` | `True` | `True` | `False` |
| `ALLOWED_HOSTS` | `*` | `staging.*` | `api.arcad3x.*` |
| `DATABASE_URL` | SQLite file | PostgreSQL (managed) | PostgreSQL (managed) |
| `CORS_ORIGINS` | `*` | `staging.*` | `arcad3x.*` |

### 8.5 CI/CD Pipeline (GitHub Actions)

```yaml
name: Deploy ARCAD3X

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest Tests/test_api_full.py Tests/test_security.py
      - run: pytest Tests/test_game_units.py

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pygbag
      - run: |
          cd Game_Python
          python -m pygbag main.py --ume_block=0 --can_close=1
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./Game_Python/build/web
```

### 8.6 Deployment Checklist (Go-Live)

| Step | Action | Owner | Verification Criteria |
|:---|:---|:---|:---|
| 1 | Set up PostgreSQL on Render | Melissa | Database accessible from Render service |
| 2 | Run Django migrations | Melissa | `python manage.py migrate` exits 0 |
| 3 | Create superuser account | Melissa | Can log in to `/admin` |
| 4 | Set environment variables on Render dashboard | Melissa | All required vars present |
| 5 | Verify API health endpoint | Hugo | `GET /api/docs` returns 200 |
| 6 | Build Pygbag WASM bundle locally | Hugo | `build/web/` contains `index.html` and `main.py` |
| 7 | Test WASM in browser | Hugo | Game loads in Chrome, Firefox, Safari |
| 8 | Enable GitHub Pages on repository settings | Hugo | Pages URL returns 200 |
| 9 | Push `build/web/` to `gh-pages` branch | GitHub Actions | Actions workflow exits green |
| 10 | End-to-end smoke test | Both | Register → Play → Submit Score → View Leaderboard |
| 11 | Configure custom domain (optional) | Hugo | DNS A record points to GitHub Pages |
| 12 | Write public README with game URL | Hugo | README contains playable link |

### 8.7 Rollback Strategy

| Scenario | Rollback Action | Recovery Time |
|:---|:---|:---|
| Backend bug in production | Revert commit on `main` → Render auto-deploys previous build | < 5 minutes |
| WASM bundle broken | Rollback `gh-pages` branch to last known good commit | < 2 minutes |
| Database corruption | Restore from Render automatic daily backups | < 30 minutes |
| API unreachable during event | Game continues in offline mode (local JSON); sync deferred | Immediate |

---

## Appendix A: Risk Register

| Risk | Probability | Impact | Mitigation Strategy | Owner |
|:---|:---|:---|:---|:---|
| Pygbag WASM fails on Safari/iOS | Medium | High | Test on iPhone before demo; provide `.exe` fallback link; monitor Pygbag GitHub issues for Safari compatibility patches. | Hugo |
| API unreachable during gameplay | Medium | Medium | `api_client.py` silently fails (`try/except` → `return None`); game continues, score saved locally only. Retry sync on next boot if token present. | Hugo |
| Memory leak in long sessions (>30 min) | Low | Medium | Pygame surfaces freed on state change; `del` unused sprites; profile with `tracemalloc` if performance degradation observed. | Hugo |
| Touch controls confusing for new players | Medium | Medium | Help popup (`popup_help`) explains controls on first launch; in-game HUD shows button zones with subtle outlines. | Hugo |
| Asset loading failure (missing PNG) | Low | High | `load_image()` returns a colored placeholder rectangle if file missing; game does not crash. Log warning to console. | Hugo |
| JWT secret compromise | Low | High | Rotate `JWT_SECRET_KEY` via Render dashboard; invalidate all active tokens; force re-login for all users. | Melissa |
| Database connection pool exhaustion | Low | High | Gunicorn worker count tuned to PostgreSQL connection limit; implement connection pooling with `pgbouncer` if scaling beyond MVP. | Melissa |

---

*Document Version: 2.0 — Hugo Ramos — Game Client & Integration Lead*  
*Last Updated: May 27, 2025*  
*Review Cycle: Per-sprint or upon major architectural change*
