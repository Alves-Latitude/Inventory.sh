# Guia de Instalação — Inventário DC

## Pré-requisitos no servidor Linux

- Docker >= 24
- Docker Compose >= 2.20

## Primeiro deploy

```bash
# 1. Copie o arquivo de variáveis e edite com seus valores
cp .env.example .env
nano .env          # edite SECRET_KEY, DB_PASSWORD, EMAIL_*, etc.

# 2. Suba os containers
docker compose up -d --build

# 3. Aplique as migrations e crie dados iniciais
docker compose exec web python manage.py migrate
docker compose exec web python manage.py setup_inicial

# 4. Acesse o sistema
# http://<IP-do-servidor>/
# Login: admin | Senha: admin123  ← TROQUE IMEDIATAMENTE
```

## Atualizações futuras

```bash
git pull
docker compose up -d --build
docker compose exec web python manage.py migrate
```

## Backup do banco de dados

```bash
docker compose exec db pg_dump -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d).sql
```
