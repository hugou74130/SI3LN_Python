# ARCAD3X — Demo Day Speaker Notes (Solo, Simple English, 8 min)

Presenter: **Hugo Ramos** (solo). Mélissa is credited on the slides but does not present.
Total runtime: **8:00**. Notes are also embedded in `ARCAD3X_DemoDay.pptx` (Presenter View).
Style: short simple sentences for a beginner English speaker. Say them slowly and clearly.

---

## Slide 1 — Title & Names · `0:00 – 0:20` (20s)
Hello everyone. My name is Hugo Ramos.
This project is ARCAD3X. It is an arcade game with data tracking.
The game is called Space Invaders 3: Last Night. I built it with Mélissa Sbibih.
In eight minutes, I will show you our full-stack project.

## Slide 2 — Team & Roles · `0:20 – 1:00` (40s)
First, the team. We are two full-stack game developers.
I worked on the gameplay, the visuals, and the speed of the game. I also did the Docker part and the deployment.
Mélissa worked on the architecture and the data. She also did the documentation and the tests.
The project has three parts: a 2D arcade game, a secure REST API with login, and a web dashboard for stats.
Docker Compose runs everything together.

## Slide 3 — Inspiration · `1:00 – 1:45` (45s)
Where did the idea come from? Classic arcade games are fun. But when you die, everything is lost.
No score history. No progress. You cannot compare with other players.
So we mixed two things: the fun of arcade games, and the power of data.
Now you can save scores, compare players, and see your progress.
We built it in three steps. V1 was only the game in Pygame. V2 added login and scores. V3 is the full stack: API, database, and dashboard.

## Slide 4 — Technology & Architecture · `1:45 – 2:45` (60s)
This is our technology. We use Python and Pygame for the game. It is fast and good for 2D.
With Pygbag, the game runs in the browser. No install needed.
For the backend, we use Django Ninja. It gives automatic API docs and data checking.
We store data in PostgreSQL 15. It is strong and ready for production.
Redis 7 handles the token blacklist and blocks too many requests.
For login, we made our own JWT system. It uses SHA-256 with a pepper, and token rotation.
The dashboard is simple JavaScript. No build step.
And everything runs in four Docker services, with one command.

## Slide 5 — Core Algorithms & Code · `2:45 – 3:45` (60s)
Here is some code. Top left: the JWT token. We create a token with the user id and a 24-hour timer.
Below: the security facade. Before we send data, we remove secret keys like password and token. This is extra safety.
On the right: the player in the game. It has a sprite, a speed, five lives, a shield, and a special attack.
And the API endpoint. A user with a token sends their score and level, and we save the game session.
Simple, safe, and checked.

## Slide 6 — Docker Architecture · `3:45 – 4:15` (30s)
This is how it works together. Nginx is the front door on port 80.
It sends `/api` to Django, `/wasm` to the game, and `/dashboard` to the web app.
The dashboard gets data from the API with a token. Django talks to PostgreSQL and Redis.
Four containers. One command.

## Slide 7 — Process, Collaboration & Timeline · `4:15 – 5:05` (50s)
We worked in six phases. Phase 1: a simple game with menu, lives, and collisions.
Phase 2: login and guest mode. Phase 3: the Django API with PostgreSQL and JWT.
Phase 4: the dashboard with leaderboard and profiles. Phase 5: Docker, WASM, and tests.
Phase 6: more features like shield, sound, and keybindings.
Some numbers: **85 commits**, about **32 thousand lines of code**, **68 Python files**, **19 test suites**, **4 Docker services**, **8 characters**, and **30 levels in 6 worlds**.

## Slide 8 — Challenges Overcome · `5:05 – 6:05` (60s)
We had five big challenges.
One: the game had to talk to the API with tokens. We made a special API client with retry and offline mode.
Two: security. We protected against XSS, IDOR, and brute-force. We used a security facade, middleware, rate limiting, and data checking.
Three: the game states. Menu, login, play, pause, game over, leaderboard. We wrote them clearly in the code.
Four: the WebAssembly build with Pygbag. We used a special Dockerfile and a shared volume.
Five: the tests. We wrote 19 test suites for auth, API, security, and more.

## Slide 9 — Learnings · `6:05 – 6:45` (40s)
What did we learn? Good things: the modular design let us work at the same time.
Clean commits gave a clean history. Docker removed the "it works on my computer" problem. Django Ninja gave free docs and checks.
What we would change: use Docker from day one. Write more tests early. Maybe use React or Vue for the dashboard. And add multiplayer sooner.
The best technical parts were the JWT system, the WASM build, and the security design.

## Slide 10 — Next Steps (Post-MVP) · `6:45 – 7:15` (30s)
What is next after the MVP? Our V3 plan:
a story mode with cinematics. New worlds like Lava and Ice. Local multiplayer on one screen.
Power-ups. Bosses at the end of each world. Daily quests. And a live leaderboard with WebSockets.

## Slide 11 — Live Demo · `7:15 – 7:45` (30s)
Now, a quick demo. This is the main menu. You can play as guest or log in.
Here you choose your character. Eight characters. Then you choose a level, by world.
In the game you see the score, the lives, and the shield. Game over shows the top 20 leaderboard.
The dashboard updates in real time. And the API docs are automatic, on `/api/docs`.
One command: `docker compose up`. Then open localhost.

## Slide 12 — Questions · `7:45 – 8:00` (15s)
So, this is ARCAD3X. Full-stack, 19 test suites, 4 Docker services, JWT security, and WASM ready.
The code is on GitHub. Thank you very much. I am happy to answer your questions.

---

### Timing cheat sheet
| Slide | End time | Budget |
|---|---|---|
| 1 | 0:20 | 20s |
| 2 | 1:00 | 40s |
| 3 | 1:45 | 45s |
| 4 | 2:45 | 60s |
| 5 | 3:45 | 60s |
| 6 | 4:15 | 30s |
| 7 | 5:05 | 50s |
| 8 | 6:05 | 60s |
| 9 | 6:45 | 40s |
| 10 | 7:15 | 30s |
| 11 | 7:45 | 30s |
| 12 | 8:00 | 15s |

**Next:** pronunciation guide for hard words (Pygbag, PostgreSQL, Nginx, facade, etc.) — ask when ready.
