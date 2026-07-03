# ARCAD3X / SI3LN — Fiches de Révision MR
> Lundi 6 juillet 2026 | Hugo Ramos

---

## FICHE 1 — Architecture Générale

### C'est quoi ARCAD3X ?
Plateforme gaming full-stack en 3 modules :
- **Game_Python** → jeu d'arcade 2D (Pygame)
- **api/** → API REST sécurisée (Django Ninja + PostgreSQL)
- **web_dashboard/** → dashboard SPA analytics (HTML/CSS/JS vanilla)

### Flux de données (à savoir raconter)
```
Joueur joue → Game_Python envoie score à l'API via HTTP+JWT
             → API stocke en PostgreSQL
             → Dashboard lit le leaderboard via l'API
             → Joueur voit ses stats en temps réel
```

### Pourquoi 3 modules séparés ?
- **Séparation des responsabilités** : chaque module a un rôle unique
- **Développement parallèle** : Hugo sur le jeu, Melissa sur l'API → pas de conflits
- **Scalabilité** : chaque service peut évoluer indépendamment

### Docker Compose — 5 services
| Service | Port | Rôle |
|---------|------|------|
| PostgreSQL 15 | :5432 | Base de données production |
| Redis 7 | :6379 | Rate limiting + token blacklist |
| Django API | :8000 | REST API + admin |
| Nginx | :80 | Reverse proxy + fichiers statiques |
| Pygbag | — | Compile le jeu Pygame → WebAssembly |

**Pourquoi Docker ?** → Environnement reproductible, un seul `docker compose up --build`, zéro "ça marche chez moi".

---

## FICHE 2 — Base de Données & Relations

### Modèles principaux
```
User (Django auth)
  └── Player (OneToOne) → profil de jeu
        ├── GameSession (OneToMany) → chaque partie jouée
        │     └── World (ManyToOne) → monde/thème de la session
        └── PlayerAchievement (OneToMany)
              └── Achievement (ManyToOne)
```

### Types de relations — définitions

**OneToOne (User → Player)**
> Un user a exactement un profil Player. Si on supprime le User, le Player est supprimé (CASCADE).
> `user = models.OneToOneField(User, on_delete=models.CASCADE)`

**OneToMany (Player → GameSession)**
> Un Player peut avoir des dizaines de sessions. Une session appartient à un seul Player.
> `player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='sessions')`

**ManyToOne (GameSession → World)**
> Plusieurs sessions peuvent se passer dans le même monde.
> `world = models.ForeignKey(World, on_delete=models.SET_NULL, null=True)`

**ManyToMany (Player ↔ Achievement)** via `PlayerAchievement`
> Un joueur peut avoir plusieurs achievements, un achievement peut être gagné par plusieurs joueurs.
> Table pivot `PlayerAchievement` avec `earned_at`.

### on_delete — pourquoi c'est important ?
- `CASCADE` : supprime les enfants quand le parent est supprimé (sessions supprimées si Player supprimé)
- `SET_NULL` : met la FK à NULL (session garde son score même si le World est supprimé)
- `PROTECT` : interdit la suppression si des enfants existent

### Index DB (performances)
```python
indexes = [
    models.Index(fields=['player', '-score']),   # Leaderboard par joueur
    models.Index(fields=['world', '-score']),     # Leaderboard par monde
    models.Index(fields=['created_at']),          # Tri chronologique
]
```
→ Sans index, PostgreSQL fait un **full table scan** (O(n)). Avec index B-tree, c'est O(log n).

### MVCC — pourquoi PostgreSQL plutôt que SQLite ?
**MVCC (Multi-Version Concurrency Control)** : plusieurs lecteurs et écrivains en même temps sans se bloquer.
→ SQLite bloque toute la DB en écriture. PostgreSQL gère 100+ connexions simultanées.

---

## FICHE 3 — Authentification & JWT

### Flow complet
```
1. POST /api/auth/register → crée User + Player → retourne JWT
2. POST /api/auth/login    → vérifie password → retourne JWT
3. Requête protégée        → Header: "Authorization: Bearer <token>"
4. POST /api/auth/logout   → blackliste le token dans Redis
5. POST /api/auth/refresh  → retourne nouveau JWT (rotation)
```

### Structure d'un JWT
Un JWT = 3 parties encodées en Base64, séparées par des `.`
```
header.payload.signature

Header  : {"alg": "HS256", "typ": "JWT"}
Payload : {"user_id": 1, "username": "hugo", "exp": 1770468000, "iat": 1770381600}
Signature: HMAC-SHA256(header + "." + payload, SECRET_KEY + PEPPER)
```
→ Le **payload est lisible** (juste Base64), mais la **signature est vérifiée** par le serveur.
→ Si quelqu'un modifie le payload, la signature ne correspond plus → rejeté.

### Pourquoi JWT et pas sessions ?
- **Stateless** : le serveur n'a pas besoin de stocker les sessions
- **Scalable** : plusieurs serveurs peuvent vérifier le même token sans partager d'état
- **Expiration intégrée** : `exp` dans le payload → automatique

### Pepper vs Salt — différence
| | Salt | Pepper |
|---|------|--------|
| Stocké | Dans la DB avec le hash | Sur le serveur (env variable) |
| Par utilisateur | Oui, unique | Non, partagé |
| Protège contre | Rainbow tables | Compromission de la DB |

Notre implémentation : `HMAC-SHA256(token_payload, JWT_PEPPER)` → même si la DB est volée, sans le pepper le token ne peut pas être forgé.

### Token Blacklist (Redis)
Au logout : `SET blacklist:{token_hash} 1 EX 86400` (TTL = 24h = durée de vie du token)
À chaque requête : on vérifie que le token n'est pas blacklisté.
→ Redis est en mémoire → vérification en O(1).

---

## FICHE 4 — Hashing SHA-256 (Jeu Python)

### Pourquoi hasher les mots de passe ?
Si la DB est compromise, les mots de passe ne doivent pas être lisibles en clair.

### Comment ça marche dans le code
```python
# auth.py — Game_Python
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
```
→ `hexdigest()` retourne une chaîne hexadécimale de 64 caractères.
→ **Irréversible** : impossible de retrouver le mot de passe à partir du hash.
→ **Déterministe** : le même mot de passe donne toujours le même hash.

### Vérification au login
```python
def login(username, password):
    stored_hash = users_data[username]["password"]
    if hash_password(password) == stored_hash:
        return True  # OK
    return False  # Mauvais mot de passe
```

### Limite de SHA-256 seul
SHA-256 sans salt est vulnérable aux **rainbow tables** (tables précalculées de hash communs).
→ Dans le jeu, le risque est faible (données locales JSON). Dans l'API, on utilise JWT avec pepper.

---

## FICHE 5 — Security Facade Pattern

### C'est quoi le Facade Pattern ?
Un design pattern qui fournit une **interface simplifiée** devant un système complexe.
→ Le frontend ne touche jamais directement la DB ou les tokens bruts.

### Notre implémentation — 2 couches

**Couche 1 : `ApiFacade` (classe)**
```python
class ApiFacade:
    SENSITIVE_FIELDS = frozenset({"password", "password_hash", "secret", "raw_token"})

    def sanitize_login_response(self, raw_response):
        # Remplace le JWT brut par un session_id opaque
        token = raw_response.get("token", "")
        return {
            "ok": True,
            "username": raw_response.get("username"),
            "player_id": raw_response.get("player_id"),
            "session_id": hashlib.sha256(f"{token[:16]}:{time.time()}".encode()).hexdigest()[:32]
        }
```
→ Le frontend ne voit **jamais** le JWT brut.

**Couche 2 : `SecurityFacadeMiddleware` (Django middleware)**
```python
class SecurityFacadeMiddleware:
    def __call__(self, request):
        response = self.get_response(request)
        # Headers de sécurité automatiques
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "SAMEORIGIN"
        # Sanitize toutes les réponses JSON /api/*
        if request.path.startswith("/api/") and "application/json" in response.content_type:
            data = json.loads(response.content)
            response.content = json.dumps(_sanitize(data)).encode()
        return response
```
→ **Filet de sécurité** : même si un endpoint oublie de filtrer, le middleware nettoie.

### Pourquoi ce pattern ?
- **Défense en profondeur** : 2 couches indépendantes
- **Centralisation** : la logique de sanitisation est à un seul endroit
- **Testabilité** : on peut tester `ApiFacade` indépendamment des endpoints

---

## FICHE 6 — Rate Limiting (Redis)

### C'est quoi le Rate Limiting ?
Limiter le nombre de requêtes qu'un client peut faire sur une période donnée.
→ Protège contre les attaques **brute-force** (essayer 1000 mots de passe) et **DoS**.

### Notre configuration
- Endpoints d'auth : **30 requêtes / 60 secondes** par IP
- Changement de mot de passe : **5 requêtes / 60 secondes** par IP

### Comment Redis implémente ça
```
# Clé Redis : "ratelimit:{ip}:{endpoint}"
# Valeur : compteur avec TTL

INCR ratelimit:192.168.1.1:login
EXPIRE ratelimit:192.168.1.1:login 60

# Si compteur >= 30 → retourner HTTP 429 Too Many Requests
```
→ Redis en mémoire → vérification en **sous-milliseconde**.

### Pourquoi Redis plutôt qu'un dict Python en mémoire ?
- Python dict : perdu si le serveur redémarre, ne fonctionne pas sur plusieurs instances
- Redis : persistant, partagé entre tous les workers Django, TTL natif

---

## FICHE 7 — Django Ninja / REST API

### Pourquoi Django Ninja ?
- **Django** : ORM, admin, migrations, auth intégrés
- **Ninja** (sur Django) : validation **Pydantic** automatique, docs **OpenAPI/Swagger** auto-générées sur `/api/docs`
- **Type-safe** : les schémas définissent exactement ce qui entre et sort

### Schéma Pydantic
```python
# schemas.py
from ninja import Schema

class ScoreIn(Schema):
    score: int
    level_reached: int
    world_id: int

class SessionOut(Schema):
    id: int
    score: int
    level_reached: int
    completed: bool
```
→ Si le client envoie `score: "abc"` → Pydantic retourne automatiquement **HTTP 422 Unprocessable Entity**.
→ Pas besoin d'écrire la validation manuellement.

### Endpoint typique
```python
@router.post("/sessions", auth=JWTAuth())
def create_session(request, data: ScoreIn):
    session = GameSession.objects.create(
        player=request.auth,         # User injecté par JWTAuth()
        score=data.score,
        level_reached=data.level_reached,
        world_id=data.world_id,
    )
    return {"id": session.id, "score": session.score}
```

### CRUD — verbes HTTP
| Méthode | Action | Exemple |
|---------|--------|---------|
| GET | Lire | `GET /api/game/players` |
| POST | Créer | `POST /api/game/sessions` |
| PUT | Remplacer | `PUT /api/game/players/1` |
| PATCH | Modifier partiel | `PATCH /api/game/sessions/1` |
| DELETE | Supprimer | `DELETE /api/game/players/1` |

### Codes HTTP importants
- `200` OK, `201` Created, `204` No Content
- `400` Bad Request, `401` Unauthorized, `403` Forbidden
- `404` Not Found, `409` Conflict, `422` Unprocessable Entity
- `429` Too Many Requests, `500` Internal Server Error

---

## FICHE 8 — IDOR & Sécurité Autorisation

### C'est quoi IDOR ?
**Insecure Direct Object Reference** : accéder aux données d'un autre utilisateur en changeant un ID.
```
GET /api/game/sessions/1  → mes sessions
GET /api/game/sessions/2  → sessions d'un autre joueur  ← IDOR
```

### Notre protection
```python
@router.get("/sessions/{session_id}", auth=JWTAuth())
def get_session(request, session_id: int):
    session = get_object_or_404(GameSession, id=session_id)
    # Vérifie que la session appartient bien à l'utilisateur connecté
    if session.player.user != request.auth:
        raise HttpError(403, "Forbidden")
    return session
```
→ Même si l'ID est deviné, l'API vérifie que la ressource **appartient** à l'utilisateur authentifié.

---

## FICHE 9 — Frontend SPA (Dashboard)

### C'est quoi une SPA ?
**Single Page Application** : une seule page HTML, le routing est géré en JavaScript.
→ Pas de rechargement de page complet → expérience fluide.

### Notre architecture
```javascript
// app-refactored.js — AppManager
class AppManager {
    navigate(page) {
        history.pushState({}, '', `/${page}`);
        this.renderPage(page);
    }
    renderPage(page) {
        switch(page) {
            case 'leaderboard': this.showLeaderboard(); break;
            case 'profile':     this.showProfile();     break;
            // ...
        }
    }
}
```

### Security Facade côté JS
```javascript
// api-facade.js
async function getLeaderboard(worldId = null, limit = 10) {
    let url = `/api/game/leaderboard?limit=${limit}`;
    if (worldId) url += `&world_id=${worldId}`;
    const res = await fetch(url, {
        headers: { "Authorization": `Bearer ${getToken()}` }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
}
```
→ Toutes les requêtes passent par `api-facade.js` → un seul endroit pour gérer l'auth, les erreurs, etc.

### Internationalisation (i18n)
```javascript
// i18n.js
const translations = {
    en: { leaderboard: "Leaderboard", score: "Score" },
    fr: { leaderboard: "Classement", score: "Score" }
};
function t(key) {
    return translations[currentLang][key] || key;
}
```

---

## FICHE 10 — Pygame & Architecture du Jeu

### Game Loop
```python
# game.py
while running:
    # 1. Handle events (input)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Update state
    player.update(keys)
    enemies.update()
    bullets.update()
    check_collisions()

    # 3. Draw
    screen.fill(BLACK)
    player.draw(screen)
    enemies.draw(screen)
    pygame.display.flip()

    # 4. Cap FPS
    clock.tick(FPS)  # FPS = 60
```
→ Ce pattern **Input → Update → Draw** est universel dans les jeux.

### State Machine
Le jeu a des états explicites :
```
MENU → AUTH → CHARACTER_SELECT → LEVEL_SELECT → GAMEPLAY → PAUSE → GAME_OVER
                                                               ↓
                                                          VICTORY
```
→ Chaque état a son propre `update()` et `draw()`.

### Entités (POO)
```python
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character_index=0):
        super().__init__()
        self.image = load_character(character_index)
        self.rect = self.image.get_rect(center=(x, y))
        self.lives = MAX_LIVES   # 5
        self.shield = 0
        self.score = 0

class Enemy(pygame.sprite.Sprite): ...
class Bullet(pygame.sprite.Sprite): ...
```
→ `pygame.sprite.Sprite` : gestion automatique des groupes, collisions, et rendu.

### Collisions
```python
# Détection joueur ↔ bullets ennemies
hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
for hit in hits:
    if player.shield > 0:
        player.shield -= 1  # Absorbe avec le shield
    else:
        player.lives -= 1   # Perd une vie
```

### Communication Jeu → API
```python
# api_client.py
class APIClient:
    def start_session(self, world_id):
        response = requests.post(
            f"{self.base_url}/api/game/sessions",
            json={"world_id": world_id},
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=5
        )
        return response.json().get("id")  # session_id
```
→ Si l'API est inaccessible → **fallback mode offline** (scores sauvegardés en JSON local).

---

## FICHE 11 — Tests

### Nos 18 suites de tests
| Catégorie | Fichier | Ce que ça teste |
|-----------|---------|----------------|
| Game Units | `test_game_units.py` | utils, auth, scores, api_client (43 tests, OFFLINE) |
| Auth | `test_authentication.py` | register, login, logout, token |
| API | `test_api_full.py` | tous les endpoints CRUD |
| Sécurité | `test_security.py` | XSS, injection, CORS, IDOR |
| E2E | `test_e2e_flow.py` | flux complet joueur → API → leaderboard |
| Perf | `test_performance.py` | temps de réponse < 200ms, 10 requêtes concurrentes |
| Rate limit | `test_rate_limiting.py` | 30 req/60s bloqué au 31ème |
| Avatar | `test_avatar_edge_cases.py` | SVG malicieux, mauvais MIME, fichier trop grand |

### Comment on a testé (à expliquer oralement)
1. **Tests unitaires** (`test_game_units.py`) : chaque module Python testé en isolation, sans serveur
2. **Tests d'intégration** : API + DB ensemble via Docker
3. **Tests de sécurité** : tentatives d'injection, XSS, accès IDOR — vérification que l'API rejette
4. **Tests E2E** : simulation d'un vrai parcours joueur (register → login → créer session → score → leaderboard)

### Lancer les tests
```bash
# Tests offline (43 tests)
SDL_AUDIODRIVER=dummy .venv/bin/python Tests/test_game_units.py

# Tous les tests (Docker requis)
cd Tests/ && python run_all_tests.py

# Suite spécifique
python run_all_tests.py --security
```

---

## FICHE 12 — Git & Bonnes Pratiques

### Notre workflow (Simplified Git Flow)
```
master (stable)
  ↑
  └── feature/auth-system    → PR → code review → merge
  └── feature/django-api     → PR → code review → merge
  └── feature/dashboard-spa  → PR → code review → merge
  └── fix/audio-crash        → PR → code review → merge
```

### Conventional Commits
```
feat: add JWT token refresh endpoint
fix: correct IDOR check on session endpoint
docs: update README with DB diagram
test: add security test suite for XSS
refactor: extract facade sanitize logic
chore: remove staticfiles from git tracking
```
→ Permet de générer un **CHANGELOG automatique** et de comprendre l'historique d'un coup d'œil.

### Code Review
- **Double review** : les 2 membres approuvent chaque PR
- Ce qu'on vérifie : logique, sécurité, style, tests associés, documentation

### Gitignore — ce qu'on exclut
```
.env          # secrets (SECRET_KEY, JWT_PEPPER)
*.pyc         # bytecode compilé
staticfiles/  # généré par collectstatic
db.sqlite3    # DB locale de dev
venv/         # dépendances Python
```

---

## FICHE 13 — Questions Pièges Fréquentes

**Q : Quelle est la différence entre authentification et autorisation ?**
> **Auth**entification = vérifier qui tu es (login + JWT)
> **Autor**isation = vérifier ce que tu as le droit de faire (IDOR check, `if session.player.user != request.auth`)

**Q : Pourquoi stocker les scores en PostgreSQL ET en JSON local ?**
> PostgreSQL = source de vérité pour le leaderboard global (API)
> JSON local = fallback si l'API est hors ligne + historique local du jeu standalone

**Q : Qu'est-ce que le MVCC de PostgreSQL ?**
> Multi-Version Concurrency Control : PostgreSQL crée une "snapshot" de la DB pour chaque transaction. Les lecteurs ne bloquent pas les écrivains. Essentiel pour une API avec 10+ requêtes simultanées.

**Q : Pourquoi Pygbag/WebAssembly ?**
> Pygbag compile le code Python/Pygame en WASM (WebAssembly) → le jeu tourne dans le navigateur sans installer Python. Nginx sert les fichiers WASM comme des assets statiques.

**Q : C'est quoi un middleware Django ?**
> Code qui s'exécute pour chaque requête/réponse, avant/après la vue. Notre `SecurityFacadeMiddleware` ajoute des headers de sécurité et sanitize les réponses JSON sur toutes les routes `/api/*`.

**Q : Pourquoi vanilla JS pour le dashboard et pas React/Vue ?**
> Pas de build step, déploiement immédiat via Nginx, pile cohérente avec le projet Python. La complexité de l'UI ne justifiait pas l'ajout d'un framework frontend.

**Q : Comment tu gères les erreurs de réseau dans le jeu ?**
> `api_client.py` utilise `try/except requests.exceptions.ConnectionError` + timeout de 5 secondes. Si l'API est inaccessible, le jeu passe en mode offline (scores sauvegardés localement en JSON).

**Q : C'est quoi un index de base de données et quand l'utiliser ?**
> Structure B-tree qui accélère les recherches. On indexe les colonnes fréquemment utilisées en `WHERE`, `ORDER BY`, ou `JOIN`. On a indexé `(player, -score)` pour le leaderboard par joueur et `(world, -score)` pour le leaderboard par monde.

**Q : C'est quoi la magic-byte validation ?**
> Chaque format de fichier commence par des octets spécifiques (PNG : `\x89PNG`, JPEG : `\xFF\xD8\xFF`). On lit les premiers octets du fichier uploadé pour vérifier que c'est bien une image — même si le MIME type menteur dit "image/png".

---

## Check-list Démo MR

- [ ] `docker compose up --build` → tout démarre
- [ ] Accès dashboard : http://localhost
- [ ] Accès API docs : http://localhost:8000/api/docs
- [ ] Demo : créer un compte sur le dashboard
- [ ] Demo : jouer une partie (jeu Python ou WASM)
- [ ] Demo : voir le leaderboard mis à jour
- [ ] Montrer le code : `facade.py`, `models.py`, `auth.py`, `api_client.py`
- [ ] Montrer les tests : `Tests/run_all_tests.py --game-units`
- [ ] Montrer le README : architecture diagram, DB diagram
- [ ] Montrer `SPRINTS.md` : planification, vélocité, retros
- [ ] Montrer git log : conventional commits, branches `feature/*`
