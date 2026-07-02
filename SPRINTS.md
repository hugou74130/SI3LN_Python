# ARCAD3X / SI3LN — Sprint Planning

> Agile methodology applied across 6 phases of development.
> Team: Hugo Ramos & Melissa Sbibih | Tool: GitHub Projects + Discord

---

## Sprint Overview

| Sprint | Period | Theme | Status |
|--------|--------|-------|--------|
| Sprint 1 | Oct 2025 (week 1–2) | Core Game MVP | ✅ Done |
| Sprint 2 | Oct 2025 (week 3–4) | Auth & Scores | ✅ Done |
| Sprint 3 | Nov–Dec 2025 | REST API + Database | ✅ Done |
| Sprint 4 | Jan–Feb 2026 | Security & JWT | ✅ Done |
| Sprint 5 | Mar–Apr 2026 | Web Dashboard SPA | ✅ Done |
| Sprint 6 | May–Jun 2026 | Docker, Tests & Polish | ✅ Done |

---

## Sprint 1 — Core Game MVP (Oct 2025, weeks 1–2)

**Goal:** Playable Space Invaders prototype in Pygame.

### MoSCoW Prioritization

| Priority | Task | Assignee | Status |
|----------|------|----------|--------|
| Must | Basic game loop (60 FPS, quit event) | Hugo | ✅ |
| Must | Player entity (movement, bounds) | Hugo | ✅ |
| Must | Enemy entities (grid formation, movement) | Hugo | ✅ |
| Must | Bullet system (player + enemy) | Hugo | ✅ |
| Must | Collision detection | Hugo | ✅ |
| Must | Lives system (5 lives) | Hugo | ✅ |
| Must | Win / Game Over screens | Melissa | ✅ |
| Should | HUD (score, lives display) | Melissa | ✅ |
| Should | Basic menu (START button) | Melissa | ✅ |
| Could | Explosion animations | Hugo | ✅ |
| Won't | Audio | — | 🔜 Sprint 6 |

**Deliverable:** Functional game executable. 7 commits on `feature/core-game`.

---

## Sprint 2 — Authentication & Scores (Oct 2025, weeks 3–4)

**Goal:** User account system and persistent score tracking.

### MoSCoW Prioritization

| Priority | Task | Assignee | Status |
|----------|------|----------|--------|
| Must | SHA-256 password hashing (`auth.py`) | Melissa | ✅ |
| Must | Register / login / guest mode | Melissa | ✅ |
| Must | JSON persistence (`users.json`, `scores.json`) | Melissa | ✅ |
| Must | Top-20 leaderboard | Hugo | ✅ |
| Must | Profile screen (change character/username/password) | Hugo | ✅ |
| Must | Level selector (world grid) | Hugo | ✅ |
| Should | 8 playable characters | Hugo | ✅ |
| Should | 5 worlds × 5 levels | Hugo | ✅ |
| Should | Fullscreen (F11) + responsive window | Melissa | ✅ |
| Could | CHANGELOG.md | Melissa | ✅ |
| Won't | Email recovery | — | 🔜 future |

**Deliverable:** V2.0 game with complete auth and score system. 12 commits.

---

## Sprint 3 — REST API + PostgreSQL (Nov–Dec 2025)

**Goal:** Django Ninja API with full CRUD for players, sessions, leaderboard.

### MoSCoW Prioritization

| Priority | Task | Assignee | Status |
|----------|------|----------|--------|
| Must | Django project setup + migrations | Melissa | ✅ |
| Must | `Player` model + endpoints (GET/POST/PUT/DELETE) | Melissa | ✅ |
| Must | `GameSession` model + endpoints | Hugo | ✅ |
| Must | `World` model + seeding | Hugo | ✅ |
| Must | Leaderboard endpoint (`GET /api/game/leaderboard`) | Hugo | ✅ |
| Must | Stats endpoint (`GET /api/game/stats`) | Melissa | ✅ |
| Must | OpenAPI docs (auto `/api/docs`) | — (Django Ninja) | ✅ |
| Should | PostgreSQL Docker service | Melissa | ✅ |
| Should | Game client `api_client.py` HTTP integration | Hugo | ✅ |
| Could | Achievement + PlayerAchievement models | Melissa | ✅ |
| Won't | Rate limiting | — | 🔜 Sprint 4 |

**Deliverable:** Functional REST API, game client sends scores to DB. 15 commits.

---

## Sprint 4 — Security & JWT Auth (Jan–Feb 2026)

**Goal:** Harden API with JWT authentication, security facade, rate limiting.

### MoSCoW Prioritization

| Priority | Task | Assignee | Status |
|----------|------|----------|--------|
| Must | Custom JWT (HS256, 24h expiry, pepper) | Melissa | ✅ |
| Must | Register / login / logout / refresh endpoints | Melissa | ✅ |
| Must | Token blacklisting on logout (Redis) | Melissa | ✅ |
| Must | `ApiFacade` — strip sensitive fields from responses | Hugo | ✅ |
| Must | `SecurityFacadeMiddleware` — auto-sanitize all responses | Hugo | ✅ |
| Must | Rate limiting: 30 req/60s auth, 5 req/60s password | Hugo | ✅ |
| Should | Magic-byte validation on avatar uploads | Melissa | ✅ |
| Should | XSS prevention (HTML tag stripping) | Hugo | ✅ |
| Should | CORS configuration | Melissa | ✅ |
| Should | IDOR protection (cross-user access) | Hugo | ✅ |
| Could | JWT_AUTH_GUIDE.md | Melissa | ✅ |

**Deliverable:** Secure API. Security test suite written. 13 commits.

---

## Sprint 5 — Web Dashboard SPA (Mar–Apr 2026)

**Goal:** Vanilla JS single-page application — leaderboard, player profiles, analytics.

### MoSCoW Prioritization

| Priority | Task | Assignee | Status |
|----------|------|----------|--------|
| Must | HTML/CSS base structure + arcade theme | Melissa | ✅ |
| Must | `api.js` raw API client | Hugo | ✅ |
| Must | `api-facade.js` security wrapper | Hugo | ✅ |
| Must | Leaderboard page with filters (world, limit) | Melissa | ✅ |
| Must | Player profile page (stats, bio, avatar) | Melissa | ✅ |
| Must | `app-refactored.js` SPA routing (AppManager) | Hugo | ✅ |
| Should | Pagination (leaderboard) | Melissa | ✅ |
| Should | `i18n.js` EN/FR internationalization | Hugo | ✅ |
| Should | `mobile.js` mobile support | Hugo | ✅ |
| Could | `search-service.js` global search | Melissa | ✅ |
| Could | Help & support pages | Melissa | ✅ |

**Deliverable:** Full SPA accessible via browser, consumes JWT-secured API. 14 commits.

---

## Sprint 6 — Docker, Tests & Polish (May–Jun 2026)

**Goal:** Containerize all services, write 18 test suites, finalize documentation.

### MoSCoW Prioritization

| Priority | Task | Assignee | Status |
|----------|------|----------|--------|
| Must | `docker-compose.yml` (5 services: PG, Redis, API, Nginx, Pygbag) | Hugo | ✅ |
| Must | `Dockerfile.pygbag` — compile game to WebAssembly | Hugo | ✅ |
| Must | Nginx config (reverse proxy + static files) | Melissa | ✅ |
| Must | 18 automated test suites (`Tests/`) | Hugo + Melissa | ✅ |
| Must | `run_all_tests.py` master test runner | Melissa | ✅ |
| Must | Root `README.md` — architecture, DB diagram, API docs | Melissa | ✅ |
| Must | `PRESENTATION_NOTES.md` — MR preparation slides | Hugo | ✅ |
| Should | Advanced gameplay: shield, special attack, SFX, keybindings | Hugo | ✅ |
| Should | Tutorial / Bootcamp world | Hugo | ✅ |
| Should | `SPRINTS.md` (this file) | Melissa | ✅ |
| Could | `Tests/results.txt` — captured test evidence | Hugo | ✅ |

**Deliverable:** One-command deployment (`docker compose up --build`), full documentation, 43/43 offline tests pass. 11 commits.

---

## Sprint Methodology

### Daily Stand-Up Format (Discord)
- What did I do yesterday?
- What will I do today?
- Any blockers?

### Definition of Done
- Feature implemented and manually tested
- Code reviewed by the other team member (PR on GitHub)
- No regression on existing features
- Relevant docs updated (README, CHANGELOG, or inline comments)

### Bug Resolution Process
1. Bug discovered → GitHub Issue opened with label `bug`
2. Assigned to responsible developer
3. Fix implemented in `fix/<issue>` branch
4. PR opened → code review → merge to `master`
5. Issue closed with reference to commit

### Velocity Tracking
| Sprint | Planned Tasks | Completed | Velocity |
|--------|--------------|-----------|----------|
| Sprint 1 | 10 | 10 | 100% |
| Sprint 2 | 11 | 11 | 100% |
| Sprint 3 | 11 | 11 | 100% |
| Sprint 4 | 11 | 11 | 100% |
| Sprint 5 | 11 | 11 | 100% |
| Sprint 6 | 11 | 11 | 100% |

---

## Retrospective Highlights

### Sprint 3 → Sprint 4
- **Went well:** Django Ninja auto-generated docs saved API documentation time
- **Challenge:** Merge conflicts on `game.py` when working in parallel on feature branches
- **Improvement:** Agreed on a clearer file ownership convention per sprint

### Sprint 5 → Sprint 6
- **Went well:** SPA routing with vanilla JS proved lightweight and fast
- **Challenge:** Pygbag/WASM has audio limitations — SDL_AUDIODRIVER=dummy workaround required
- **Improvement:** Start Docker integration earlier in the project (not just Phase 5)

### Final Retrospective
- **Went well:** Modular architecture allowed true parallel development across game/API/dashboard
- **Challenge:** Django migration conflicts when both members modified models simultaneously
- **Key lesson:** Conventional Commits + dual code review kept the `master` branch stable throughout
