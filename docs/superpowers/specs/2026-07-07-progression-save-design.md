# Sauvegarde de la progression — Design

**Date:** 2026-07-07
**Auteur:** Hugo Ramos (+ Claude)
**Statut:** En attente de revue

## Problème

En mode navigateur, la progression (mondes débloqués, niveaux terminés) n'est jamais
sauvegardée. À chaque rechargement le joueur repart de zéro et doit refaire le BootCamp.

Causes racines :
1. La persistance actuelle est conditionnée à `not guest_mode and current_user`. En
   navigateur il n'y a pas de login local (l'auth vit dans le dashboard / JWT), donc
   `current_user` est `None` → `update_user_data()` sort immédiatement.
2. Même si elle s'exécutait, l'écriture se fait dans un JSON sur le filesystem WASM,
   qui est éphémère et perdu à chaque rechargement.
3. La progression n'est suivie qu'au niveau **monde** (`unlocked_worlds`), pas par niveau.

## Objectif

- Sauvegarder la progression **côté serveur**, liée au compte (JWT), après **chaque fin
  de niveau** (victoire).
- Restaurer la progression au démarrage du sélecteur de niveaux.
- Granularité : **mondes débloqués** ET **niveau max terminé par monde**.
- **Verrouiller** les niveaux non atteints.
- Fonctionne en navigateur ; le desktop garde sa persistance JSON locale et bénéficie
  aussi du serveur quand authentifié.

## Règle de déblocage des niveaux

- Chaque monde a un `max_level` = plus haut numéro de niveau **terminé** (0 si aucun).
- Dans un monde débloqué, les niveaux `1 … max_level + 1` sont jouables ; les autres
  sont verrouillés (affichés grisés + 🔒, clic ignoré).
- Terminer le niveau N met `max_level = max(max_level, N)` et débloque donc N+1.
- Terminer le dernier niveau d'un monde débloque le monde suivant (comportement existant,
  conservé).
- BootCamp démarre à `max_level = 0` → seul le niveau 1 (tutoriel) est jouable au départ.

## Architecture

### 1. Backend (`api/game/`)

**Modèle** — nouveau champ sur `Player` :
```python
progression = models.JSONField(default=dict, blank=True)
# forme : {"unlocked_worlds": ["BootCamp", "Space"], "world_levels": {"0": 5, "1": 3}}
# clés world_levels = world_id (str), valeurs = max_level terminé
```
+ 1 migration.

**Endpoints** (tag "Progression", `auth=jwt_auth`) :
- `GET /api/game/progress` → `{"unlocked_worlds": [...], "world_levels": {...}}`
  (renvoie un défaut sûr `{"unlocked_worlds": ["BootCamp"], "world_levels": {}}`
  si vide).
- `PATCH /api/game/progress` — corps :
  `{"unlocked_worlds": [...], "world_levels": {world_id: max_level}}`.
  **Fusion monotone** :
  - `unlocked_worlds` = union avec l'existant.
  - `world_levels[w]` = `max(existant, reçu)` — ne descend jamais.
  - Met aussi à jour `boot_camp_completed` et `highest_level` pour compat avec le reste.
  - Renvoie la progression fusionnée.

Schemas Pydantic : `ProgressSchema` (réponse), `ProgressUpdateSchema` (entrée).

### 2. Pont JS (`web_dashboard/game/index.html`)

Même pattern que le leaderboard :
- Au chargement, si token présent : pré-fetch `GET /api/game/progress` → stocke le JSON
  dans `window.SI3LN_PROGRESS_CACHE`.
- `window.SI3LN_save_progress = function(json)` → `PATCH /api/game/progress` avec
  `Authorization: Bearer <token>`. Logs console explicites (succès / rejet HTTP / réseau),
  comme `SI3LN_submit_score`.
- Ces fonctions vivent sur la fenêtre parente ; le jeu (iframe) y accède via
  `platform.window.parent` (déjà géré par `_browser_win()`).

### 3. Client jeu (`Game_Python/api_client.py`)

- `get_progress()` :
  - navigateur → lit `_browser_win().SI3LN_PROGRESS_CACHE` (parse JSON), sinon `None`.
  - desktop → `GET /api/game/progress` via requests (si authentifié).
- `submit_progress(unlocked_worlds, world_levels)` :
  - navigateur → `getattr(_browser_win(), "SI3LN_save_progress")(json.dumps(payload))`,
    logs si le pont manque.
  - desktop → `PATCH /api/game/progress`.
  - Retourne `None` en navigateur (best-effort), le dict serveur en desktop.

### 4. Logique jeu (`Game_Python/level_selector.py` + `game.py`)

**`level_selector.py`** :
- Nouveau dict `self.world_max_level = {world: 0 for world in worlds}`.
- `_restore_from_server(progress)` : applique `unlocked_worlds` → `world_unlocked`, et
  `world_levels` → `world_max_level` (clés world_id → nom de monde via `WORLD_IDS` inversé).
- `is_level_unlocked(world_name, level_number)` : `True` si monde débloqué **et**
  `level_number <= world_max_level[world_name] + 1`.
- `create_level_buttons()` : marque chaque bouton verrouillé (grisé + 🔒) selon
  `is_level_unlocked`. `handle_event` ignore le clic sur un niveau verrouillé.

**`game.py`** :
- Au démarrage / ouverture du sélecteur : si `api.is_authenticated()`, appelle
  `progress = self.api.get_progress()` puis `level_selector._restore_from_server(progress)`.
- Après **chaque victoire de niveau** (les deux chemins : `trigger_game_over` victoire et
  chemin level-win, là où `_submit_leaderboard` est déjà appelé) :
  - met à jour localement `world_max_level[current_world] = max(..., current_level)` ;
  - si dernier niveau du monde → unlock monde suivant (existant) ;
  - si `api.is_authenticated()` : `self.api.submit_progress(unlocked_worlds, world_levels)`
    (best-effort, try/except avec log — même style que le correctif leaderboard).

## Flux de données

```
Fin de niveau (victoire)
  └─ game.py: maj world_max_level + unlocked_worlds (local)
       └─ api.submit_progress()  ── navigateur ─▶ window.parent.SI3LN_save_progress(json)
                                                     └─▶ PATCH /api/game/progress (JWT)
                                                           └─▶ Player.progression (fusion monotone)

Boot / ouverture sélecteur
  page /game/ pré-fetch GET /api/game/progress ─▶ window.SI3LN_PROGRESS_CACHE
  └─ game.py: api.get_progress() lit le cache
       └─ level_selector._restore_from_server() ─▶ world_unlocked + world_max_level
            └─ create_level_buttons() verrouille les niveaux > max_level+1
```

## Gestion des erreurs

- Toutes les écritures serveur sont **best-effort** : un échec réseau/API ne bloque pas
  le jeu (try/except + log console), la progression locale de la session reste correcte.
- `get_progress()` renvoyant `None` (non connecté, cache absent) → on garde le défaut
  (BootCamp niveau 1). Pas de crash.
- La fusion monotone côté serveur empêche toute régression de progression même en cas de
  requêtes en désordre ou rejouées.
- Rétro-compat : les anciens profils (sans `progression`) → défaut sûr ; le champ
  `boot_camp_completed` continue d'être honoré.

## Tests

- **Backend (pytest)** : PATCH crée/fusionne ; la fusion ne descend jamais un max ; GET
  renvoie le défaut sûr ; auth requise (401 sans JWT).
- **Client** : `is_level_unlocked` (limites : max_level, max_level+1, max_level+2) ;
  `submit_progress`/`get_progress` en mode navigateur (pont présent/absent) et desktop.
- **Bout-en-bout (navigateur headless, comme les diagnostics leaderboard)** : connexion →
  terminer un niveau → PATCH atteint le serveur → recharger → niveaux débloqués corrects,
  niveaux suivants verrouillés.

## Hors périmètre (YAGNI)

- Pas de synchronisation temps réel dashboard ↔ jeu de la progression.
- Pas d'UI de progression dédiée dans le dashboard (le jeu suffit).
- Pas de migration des scores/sessions existants vers `progression` (départ propre).
```
