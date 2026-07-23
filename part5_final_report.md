# ARCAD3X — Final Report (Portfolio Part 5)

**Project:** ARCAD3X — Arcade Analytics Platform (SI3LN — Space Invaders III Last Night)
**Team:** Hugo Ramos, Melissa Sbibih
**School:** Holberton School France
**Repository:** https://github.com/hugou74130/SI3LN_Python

---

## 1. Results Summary

### 1.1 MVP core functionalities

| Module | Delivered | Implementation |
|---|---|---|
| **Game_Python** | ✅ | Pygame 2D shoot 'em up: state machine, entities (Player, Enemy, Bullet, Bonus, Explosion), world/level selection, in-game auth, browser deployment via Pygbag/WebAssembly |
| **api** | ✅ | Django Ninja REST API — auth endpoints (register, login, logout, refresh, me, change-password, update-account) and game endpoints (players, sessions, leaderboard, stats, worlds, achievements, profile, avatar upload). Auto-generated OpenAPI docs at `/api/docs` |
| **web_dashboard** | ✅ | Vanilla JS SPA: routing via `AppManager`, leaderboard, player profiles, global search, i18n EN/FR, mobile support |
| **Persistence** | ✅ | PostgreSQL 15 — 6 entities (User, Player, GameSession, World, Achievement, PlayerAchievement) with full relational modelling |
| **Security** | ✅ | Security Facade pattern (`ApiFacade` + `SecurityFacadeMiddleware`): response sanitization, opaque session IDs in place of raw JWTs, security headers, rate limiting, token blacklisting, magic-byte validation on uploads |
| **Infrastructure** | ✅ | Docker Compose, 5 services: PostgreSQL, Redis, Django API, Nginx frontend, Pygbag builder — single-command startup |
| **Testing** | ✅ | 18 automated test suites across authentication, API, security, data validation, E2E, edge cases, game units and performance |

### 1.2 Outcomes vs. Project Charter objectives

| Initial objective | Status | Comment |
|---|---|---|
| Playable arcade game | Achieved | SI3LN fully playable, also deployed to browser via WebAssembly |
| Documented REST API | Achieved | OpenAPI auto-generated, 17+ endpoints documented in the README |
| Secure player authentication | Achieved | Custom JWT with SHA-256 pepper, rotation, expiry detection, blacklist on logout |
| Persistent multi-player leaderboard | Achieved | Filterable by world, with per-player statistics |
| Analytics dashboard | Achieved | SPA consuming the same API as the game client |
| Fully containerized environment | Achieved | `docker-compose up --build` starts the whole stack |
| Automated test coverage | Achieved | 18 suites with a colour-coded runner and per-category execution |

**MVP scope completion: 100 % of the "must have" features, plus two items initially listed as "should have" (WebAssembly build, EN/FR internationalization).**

### 1.3 Key metrics

| Indicator | Value |
|---|---|
| Docker services orchestrated | 5 |
| REST endpoints exposed | 17+ (7 auth, 10+ game) |
| Automated test suites | 18 |
| Database entities modelled | 6 |
| Tracked bugs, resolved | 5 / 5 |
| Commits on the project | 97 |
| Languages in the codebase | Python 70.9 %, JavaScript 14.2 %, HTML 7.3 %, CSS 6.6 % |
| Rate limiting enforced | 30 req/60 s (auth), 5 req/60 s (password change) |
| Interface languages supported | 2 (EN / FR) |

**User feedback during testing:** the sign-up → play → score-submission → leaderboard flow completed without blockers; testers described the dashboard navigation as intuitive and the arcade visual identity as consistent across game and dashboard.

---

## 2. Lessons Learned

### 2.1 What went well, and why

**Containerizing from day one.** Docker Compose was set up before most of the business logic. This eliminated the entire "works on my machine" class of problems, kept both team members on an identical stack, and made adding a service later (Redis, then the Pygbag builder) a matter of a few lines of configuration rather than a migration.

**Django Ninja over Django REST Framework.** Pydantic schemas served three purposes at once — request validation, response serialization, and documentation. The auto-generated OpenAPI spec at `/api/docs` could never drift out of sync with the code, which removed a whole category of front/back miscommunication.

**The Security Facade pattern.** Centralizing sanitization in `facade.py` plus a middleware safety net meant security was not re-implemented endpoint by endpoint. When the SVG-upload vulnerability was found, the fix landed in one place and covered every route.

**One API, two very different clients.** The Pygame client and the JS dashboard consume the same endpoints. This forced the API to stay genuinely generic instead of being shaped around a single frontend, and it let both clients be developed in parallel.

**Feature-Driven Pairing and dual review.** Designing, implementing and testing each feature as a pair — with every PR requiring both approvals — caught defects early and meant neither team member had blind spots in the codebase.

### 2.2 Challenges faced and how they were addressed

| Challenge | Impact | Resolution |
|---|---|---|
| Race condition: the game client sent a score before the session existed | Scores silently lost — high severity | Sequential flow enforced in `api_client.py`; session creation now awaited before any score submission |
| Avatar upload accepted SVG files with embedded JavaScript | Stored XSS vector — high severity | Magic-byte validation plus a strict MIME whitelist, applied at the facade level |
| Tokens not blacklisted on logout with Redis < 7 | Sessions remained valid after logout | Redis pinned to version 7 in `docker-compose.yml` |
| SDL audio crash on headless server | API container failed to start in CI-like environments | `SDL_AUDIODRIVER=dummy` set for headless contexts |
| Mermaid diagrams broken by quoted edge labels | Architecture documentation unreadable on GitHub | Label syntax corrected (commit `91d220e`) |
| Deploying a Pygame client to the browser | Pygbag imposes constraints absent from desktop Pygame (async loop, asset loading) | Game loop restructured to be Pygbag-compatible; builder isolated as its own Docker service |

### 2.3 How the team can improve on future projects

1. **Write integration tests alongside features, not in a dedicated late phase.** The 18 suites are a real strength, but several were written after the fact — the race condition on session creation would have been caught days earlier by an E2E test written with the feature.
2. **Threat-model file uploads before implementing them.** The SVG vulnerability was a known class of attack; a five-minute checklist at design time would have prevented it entirely.
3. **Pin infrastructure versions from the start.** The Redis blacklist bug came from an unpinned image, not from application code. Pinning is free; debugging a version-dependent behaviour is not.
4. **Budget explicitly for integration.** Feature development was estimated accurately; wiring the three modules together was not, and absorbed more time than planned.
5. **Keep a living record of deliberate trade-offs.** Distinguishing "not done" from "done differently, on purpose" changes how a reviewer reads the project — and it is much harder to reconstruct at presentation time than to write down as it happens.

---

## 3. Team Retrospective — Key Points

Retrospective held at the end of the project around three guiding questions. Sprint-level retrospectives are documented in [`SPRINTS.md`](../SPRINTS.md).

### What worked well as a team

- **Feature-Driven Pairing:** every feature designed, implemented and tested as a pair. Slower per feature, but almost no rework and no single-owner knowledge silos.
- **Simplified Git Flow:** stable `master`, `feature/*` branches, Conventional Commits. 97 commits with a readable history and very few merge conflicts.
- **Dual code review:** mandatory approval from both members on every pull request — the main reason no critical bug reached the final demo.
- **Daily syncs on Discord:** short, regular, and enough to keep two parallel workstreams aligned without heavy process.

### Challenges we faced, and how we resolved them

- **Scope ambiguity early on** → resolved by MoSCoW prioritization, freezing an explicit "must have" list and pushing everything else to post-MVP.
- **Two different runtime environments (desktop game vs. web stack)** → resolved by containerizing everything, including the WebAssembly builder.
- **End-of-project time pressure** → resolved by an explicit priority rule: demo stability before new features. No feature was added in the final stretch.
- **Bug triage across three modules** → resolved by tracking every defect as a GitHub Issue with a severity level, rather than discussing them informally.

### How we can improve collaboration in the future

- Introduce a lightweight **ADR format** to record architecture decisions as they are made, instead of reconstructing the reasoning at presentation time.
- Add **CI on pull requests** so the 18 test suites run automatically rather than on demand — dual review is strong, but it does not replace an automated gate.
- Alternate pairing roles more deliberately, so both members drive the parts of the stack they are less comfortable with.
- Hold a **short retrospective at the end of each sprint**, not only at the end of the project — several lessons above were visible mid-project and could have been applied immediately.

---

## 4. Conclusion and Next Steps

ARCAD3X delivers what the charter set out: a complete gaming ecosystem where a Pygame arcade client, a documented REST API and an analytics dashboard interoperate inside a reproducible, containerized environment — with security treated as an architectural concern rather than an afterthought, and with 18 automated test suites backing the whole.

**Identified next steps:**

1. **CI/CD pipeline** — run the test suites automatically on every pull request
2. **Distributed rate limiting** — ensure limits hold across multiple API workers, not per process
3. **Full RBAC** — a proper administrator role beyond ownership-based access checks
4. **New games on the existing API** — the leaderboard, achievement and session models are game-agnostic by design; adding a second title should require no backend change
5. **Public deployment** — host the WebAssembly build so the game is playable without any local setup
