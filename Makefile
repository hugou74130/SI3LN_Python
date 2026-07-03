# SI3LN – Shortcuts
# Usage: make <target>

COMPOSE  = docker compose -f Docker/docker-compose.yml
GAME_DIR = Game_Python

.PHONY: up down build rebuild logs game restart-frontend shell-api migrate

## Start all services (detached)
up:
	$(COMPOSE) up -d

## Stop all services
down:
	$(COMPOSE) down

## Build + start (first run or after API/infra changes)
build:
	$(COMPOSE) up --build -d

## Full rebuild from scratch (images + volumes reset)
rebuild:
	$(COMPOSE) down -v
	$(COMPOSE) up --build -d

## Stream logs for all services
logs:
	$(COMPOSE) logs -f

## Build the browser game locally (no Docker needed), then reload nginx
game:
	cd $(GAME_DIR) && pygbag --build main.py
	sed -i 's|https://pygame-web.github.io/archives/0.9/|/pygbag-cdn/|g' $(GAME_DIR)/build/web/index.html
	python3 $(GAME_DIR)/patch_index.py $(GAME_DIR)/build/web/index.html
	$(COMPOSE) restart frontend
	@echo ""
	@echo "=========================================="
	@echo "  Game built! Open: http://localhost/game/"
	@echo "=========================================="

## Reload nginx without rebuilding the game
restart-frontend:
	$(COMPOSE) restart frontend

## Open a shell in the API container
shell-api:
	$(COMPOSE) exec api bash

## Run Django migrations inside the API container
migrate:
	$(COMPOSE) exec api python manage.py migrate
