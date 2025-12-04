# Supabase Setup Guide

Use this guide when deploying Threatconnectome in an on-premises environment backed by Supabase. Follow the general [Setup Guide](setup.md) first, then apply the Supabase-specific steps below.

## Environment variables

Copy the Supabase template, rename it to `.env`, and edit the values.

```bash
cp .env.supabase.example .env
vi .env  # update defaults
```

### Required variables

- `SUPABASE_POSTGRES_PASSWORD` – password for the Supabase Postgres instance
- `JWT_SECRET` – JSON Web Token secret
- `ANON_KEY`
- `SERVICE_ROLE_KEY` – Supabase service-role API key
- `DASHBOARD_USERNAME` – Supabase dashboard username
- `DASHBOARD_PASSWORD` – Supabase dashboard password
- `LOGFLARE_API_KEY`

Place the authentication credential JSON at the path specified by `FIREBASE_CRED` if you also need Firebase compatibility.

## Production environment variables

When preparing a production build of the web UI, copy the Supabase template into the web directory and adjust the values.

```bash
cd ./web
cp .env.supabase.example .env.production.local
vi .env.production.local
```

Key values:

- `VITE_AUTH_SERVICE` – authentication service (fixed to `supabase`)
- `VITE_SUPABASE_URL` – URL exposed by the Kong container (not the auth container)
- `VITE_SUPABASE_ANON_KEY` – match the `ANON_KEY` defined in `../.env`

## Docker Compose (local stack)

Start the Supabase-based stack and run database migrations.

```bash
cd ..
sudo docker compose -f docker-compose-supabase-local.yml up -d --build
sudo docker compose -f docker-compose-supabase-local.yml exec api sh -c "cd app && alembic upgrade head"
```

Stop the stack when you are done.

```bash
sudo docker compose -f docker-compose-supabase-local.yml down
```

## Web UI development variables

When developing against Supabase, use the Supabase-specific environment template.

```bash
cd ./web
cp .env.supabase.local .env
vi .env
```

## Containers in the Supabase stack

| Container name  | Description           |
| --------------- | --------------------- |
| supabase-auth   | Authentication server |
| supabase-db     | PostgreSQL database   |
| supabase-studio | Dashboard             |
| supabase-kong   | API gateway           |
| supabase-meta   | PostgreSQL API server |
