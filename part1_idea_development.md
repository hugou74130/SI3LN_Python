# ARCAD3X — Idea Development (Portfolio Part 1)

**Team:** Hugo Ramos, Melissa Sbibih
**School:** Holberton School France
**Project repository:** https://github.com/hugou74130/SI3LN_Python

> ⚠️ **À VÉRIFIER AVANT PUBLICATION** — les idées listées en section 2 doivent correspondre à ce que vous avez réellement envisagé avec Melissa. Remplace celles qui ne collent pas ; la structure et les critères peuvent rester tels quels.

---

## 1. Team Formation & Roles Definition

### 1.1 Team members

| Member | Background & strengths | Interests |
|---|---|---|
| **Hugo Ramos** | Low-level programming, emulation and reverse engineering, game development, performance optimization | Game feel, real-time rendering, visual craftsmanship |
| **Melissa Sbibih** | System architecture, data modelling, API design, technical writing | Clean data flows, documentation, developer experience |

### 1.2 Initial roles

| Role | Holder | Rationale |
|---|---|---|
| Temporary Project Manager (Stage 1) | Melissa Sbibih | Strongest on planning and documentation, which is what Stage 1 is mostly made of |
| Game client lead | Hugo Ramos | Prior experience with game loops, sprites and performance tuning |
| API & data model lead | Melissa Sbibih | Prior experience with relational modelling and REST design |
| Frontend / dashboard | Shared | Neither member wanted to specialize away from it — deliberately kept collaborative |
| QA & testing | Shared | Each member tests the other's feature before merge |

**Why these roles.** With a two-person team, strict specialization is a liability: if one person owns a layer entirely, the other cannot review it meaningfully and the project has two single points of failure. We therefore assigned *leads* rather than *owners* — the lead makes the design calls in their area, but both members write code in every layer.

### 1.3 Team norms

**Communication**
- Discord as the single channel (voice for pairing, text for async updates)
- Daily asynchronous stand-up: what I did, what I'm doing, what blocks me
- No decision taken in a private message — anything architectural goes in a channel where it can be found again

**Collaboration**
- **Feature-Driven Pairing:** each feature is designed, implemented and tested across all three layers (game, API, dashboard) by both members, rather than split front/back
- Pair programming with frequent driver/navigator switching
- No "my code / your code" — shared ownership of the whole repository

**Decision-making**
- Technical decisions require agreement from both members; if there is no agreement, the option that is cheaper to reverse wins
- Every architectural decision is written down with its rationale
- Git: stable `master`, `feature/*` branches, Conventional Commits, and **merge only after both approve**

### 1.4 Stakeholders

| Stakeholder | Interest in the project | Influence | Impact on our work |
|---|---|---|---|
| Teaching team (Rami & pedagogical staff) | Curriculum alignment, validation, grading | High | Defines deliverables and deadlines; drives our sprint boundaries |
| Cross-cohort peers | Shared feedback, peer review, inter-cohort collaboration | Medium | Source of external testing and design critique |
| Players / end users | Game experience, dashboard usability, feature completeness | High | Their feedback drove the tutorial level and mobile support decisions |
| Platform admins | Analytics access, user management, moderation | Medium | Justified the admin role, the stats endpoints and the settings page |

---

## 2. Brainstorming and Idea Evaluation

### 2.1 Method

Individual research first (real-world problems, industry trends, existing products), then a joint session combining:

- **Mind mapping** — starting from "what do we both actually want to build for six weeks", branching into game development, developer tooling and data visualization
- **SCAMPER** — applied mainly to the arcade-game branch. The productive operation was **Combine**: an arcade game on its own is a solved problem and teaches us little; combining it with an analytics layer turns it into a full-stack data-flow problem
- **"How Might We"** — *How might we make a player's performance visible to them instead of reducing it to a single number?*

### 2.2 Ideas generated

| # | Idea | Short description |
|---|---|---|
| 1 | **Arcade game + analytics platform** | A Space Invaders-style shooter whose every session feeds a REST API, with a dashboard turning raw sessions into leaderboards, personal bests and trends |
| 2 | Study / revision tracker | Web app for students to log study sessions and visualize progress over time |
| 3 | Local event aggregator | Platform collecting and centralizing local cultural events with filtering and recommendations |
| 4 | Collaborative recipe manager | Shared cookbook with automatic shopping list generation and portion scaling |
| 5 | Emulator/ROM tooling dashboard | Web front-end for a speedrunning toolchain (frame data, input replay, run comparison) |

### 2.3 Evaluation criteria

| Criterion | Definition | Weight |
|---|---|---|
| **Feasibility** | Can a two-person team ship a working MVP in six weeks? | High |
| **Technical alignment** | Does it exercise the full stack expected by the curriculum (client, API, database, deployment)? | High |
| **Potential impact** | Is there a real user with a real problem, beyond the grade? | Medium |
| **Scalability** | Can the architecture accept new content without being rewritten? | Medium |
| **Team motivation** | Will we still want to work on it in week 6? | Medium |

### 2.4 Ranking

| Rank | Idea | Feasibility | Tech. alignment | Impact | Scalability | Motivation | Main risk |
|---|---|---|---|---|---|---|---|
| **1** | **Arcade + analytics (ARCAD3X)** | High | **Very high** | Medium | High | **Very high** | Scope creep on game content |
| 2 | Study tracker | Very high | Medium | Medium | Medium | Low | Technically unambitious — mostly CRUD |
| 3 | Emulator/ROM tooling | Medium | High | Low (niche) | Medium | High | Audience too narrow; heavy domain prerequisites |
| 4 | Event aggregator | Medium | Medium | Medium | Low | Low | Depends on third-party data availability |
| 5 | Recipe manager | High | Low | Low | Low | Low | Saturated space, no technical challenge |

---

## 3. Decision and Refinement

**Selected MVP: ARCAD3X — Arcade Analytics Platform** (flagship game: *SI3LN — Space Invaders III Last Night*).

### 3.1 The problem it solves

Classic arcade games offer an ephemeral experience. A run ends, a number appears, and everything that produced that number — accuracy, survival time, which world, which character, whether it was an improvement — is lost. Players have no insight into their own performance, no history, and no way to situate themselves against others beyond a single high score.

### 3.2 The solution

A gaming ecosystem in which every session is a data event. The game client submits structured session data to a REST API; the API persists it; a dashboard turns it back into something readable: leaderboards filterable by world, personal bests, per-player statistics and achievements. **One product, two facets — the thrill of arcade gaming plus the introspection of analytics.**

### 3.3 Target audience

- **Primary:** casual arcade players who want their progress to be visible and comparable
- **Secondary:** competitive players and cross-cohort peers who want a leaderboard worth climbing
- **Tertiary:** platform administrators needing usage statistics and moderation tools

### 3.4 Type of application

A **multi-client web platform**, made of three deployable components:

- a **desktop and browser game client** (Python/Pygame, compiled to WebAssembly via Pygbag)
- a **REST API** (Django Ninja, PostgreSQL, Redis) with auto-generated OpenAPI documentation
- a **single-page web dashboard** (vanilla JS, served by Nginx)

The whole stack is orchestrated by Docker Compose (5 services) and starts with a single command.

### 3.5 Why this idea over the others

1. **It is the only candidate that forces a genuine end-to-end data flow.** Game client → API → database → dashboard. The study tracker and the recipe manager are single-client CRUD applications; they would not have exercised API contract design, authentication across two very different clients, or multi-service deployment.
2. **Two independent clients keep the API honest.** Because both a Pygame client and a JS dashboard consume the same endpoints, the API cannot be quietly shaped around one frontend. This was the decisive argument.
3. **The scope is genuinely divisible.** The game and the API can progress in parallel behind an agreed contract — essential for a two-person team working in pairs.
4. **Content is additive, not structural.** New worlds, characters and achievements are data, not code changes. The architecture can absorb growth without a rewrite, unlike the event aggregator whose whole value depended on external data sources we did not control.
5. **Sustained motivation.** Six weeks is long enough that boredom is a real project risk. Both members wanted to build this one.

### 3.6 Key features and SMART objectives

**Objective 1 — Playable, complete arcade game client**
Deliver a Pygame shooter with a full state machine (menu → auth → character select → level select → gameplay → pause → game over → victory), at least 5 distinct worlds and 7 playable characters, playable both on desktop and in the browser, by the end of Sprint 6.

**Objective 2 — Documented, secured REST API**
Expose at least 20 REST endpoints covering authentication, players, sessions, leaderboard, worlds and achievements, with auto-generated OpenAPI documentation, JWT authentication with token rotation and blacklisting, and rate limiting on sensitive routes — all reachable at `/api/docs` by the end of Sprint 3.

**Objective 3 — Analytics dashboard consuming the same API**
Deliver a single-page dashboard providing authentication, player profile with avatar, a leaderboard filterable by world and platform statistics, using strictly the same public API as the game client, by the end of Sprint 4.

**Objective 4 — Reproducible, tested deployment**
Ship a Docker Compose stack starting all services with one command, backed by at least 15 automated test suites covering authentication, endpoints, security and the end-to-end flow, by the end of Sprint 5.

### 3.7 Scope

**In-scope (MVP)**
- Single-player arcade game with worlds, characters, levels and a scoring system
- Account creation and JWT authentication, shared by the game client and the dashboard
- Persistent game sessions with per-player statistics
- Leaderboard filterable by world, plus platform-wide statistics
- Player profile: avatar upload, bio, display preferences
- Achievement system
- Analytics dashboard with EN/FR internationalization and mobile support
- Fully containerized deployment and an automated test suite

**Out-of-scope (deferred to V2.0)**
- Real-time multiplayer (1v1 duels)
- Third-party OAuth authentication (Google / GitHub)
- Machine-learning predictive analytics
- Public cloud deployment and a full CI/CD pipeline
- Streaming / OBS overlay integration
- Native mobile applications (the dashboard is responsive; it is not a native app)

### 3.8 Identified risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Scope creep on game content** (always one more world, one more character) | High | High | MoSCoW prioritization frozen at the start; content beyond the Must-Have list only after the API and dashboard are complete |
| **Integration left too late** — three modules that only meet in the final week | Medium | **Critical** | API contract agreed before implementation; the end-to-end flow is wired in Sprint 3, not Sprint 6 |
| **Divergent development environments** between the two members | High | Medium | Docker Compose from Sprint 1; nobody runs the stack outside containers |
| **Browser deployment (Pygbag/WASM) proves harder than expected** | Medium | Medium | Treated as a Should-Have, not a Must-Have; desktop client remains the reference target |
| **Security implemented late and superficially** | Medium | High | Security Facade designed as an architectural component from Sprint 3; dedicated security test suites |
| **Two-person team — one member unavailable** | Low | High | Shared ownership, mandatory dual review, no layer known by only one person |
| **Uneven familiarity with the stack** | Medium | Low | Pair programming with role switching, so both members write code in every layer |

---

## 4. Summary of the Idea Development Process

We formed a two-person team with complementary but deliberately overlapping profiles — Hugo on game engine and performance, Melissa on architecture and data — and chose *Feature-Driven Pairing* over the usual frontend/backend split, so that no layer of the project would be understood by only one of us.

From an individual research phase and a joint mind-mapping and SCAMPER session, five candidate ideas emerged. Ranked against feasibility, technical alignment, impact, scalability and team motivation, **ARCAD3X** came first: it was the only candidate requiring a real end-to-end data flow across a game client, a REST API, a database and a web dashboard, and the only one where two structurally different clients would consume the same API — which we judged the most valuable constraint of the whole project.

The refined MVP addresses a concrete problem: arcade performance is ephemeral and invisible to the player. ARCAD3X makes it persistent and readable. Its potential impact is twofold — for players, a run stops being a disposable number and becomes a trackable history; for us, an architecture where new games, worlds and achievements are additive data rather than structural changes, which is exactly what makes the platform worth extending after the MVP.
