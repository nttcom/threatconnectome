# Threatconnectome Setup Guide (Supabase)

Use this guide when deploying Threatconnectome in an on-premises environment backed by Supabase.

## :bangbang: Requirements

- `OS`
  - `Ubuntu 20.04+ or MacOS 12.0.1+`
- `Docker`
  - `Docker Compose`
- `Node v20+`
  - `npm v7+`

### Development environment

- `Pipenv`

## :gear: Installation

```
git clone https://github.com/nttcom/threatconnectome.git
```

### Set up environment variables

Copy the Supabase template, rename it to `.env`, and edit the values.

```bash
cp .env.supabase.example .env
vi .env  # update defaults
```

### Required variables

- `SUPABASE_POSTGRES_PASSWORD` – Password to be set for the Supabase Postgres
- `JWT_SECRET` – JSON Web Token secret
- `ANON_KEY`
- `SERVICE_ROLE_KEY` – API key of Supabase
- `DASHBOARD_USERNAME` – Username of Supabase dashboard
- `DASHBOARD_PASSWORD` – Password to be set for the Supabase dashboard
- `LOGFLARE_API_KEY` - API key of logflare

### Set up production environment variables

When preparing a production build of the web UI, copy the Supabase template into the web directory and adjust the values.

```bash
cd ./web
cp .env.supabase.example .env.production.local
vi .env.production.local
```

Key values:

- `VITE_AUTH_SERVICE` – Authentication service to be used (fixed to supabase).
- `VITE_SUPABASE_URL` – URL which the kong container (not auth container) listens to.
- `VITE_SUPABASE_ANON_KEY` – Same value with ANON_KEY in ../.env.

### CORS settings (Optional)

Adjust CORS settings in [main.py](/api/app/main.py) if required.

### Web UI

```bash
cd ./web
npm ci
npm run build  # to build what is specified in package.json
```

### Run Docker Compose

Start the Supabase-based stack and run database migrations.

```bash
cd ..
sudo docker compose -f docker-compose-supabase-local.yml up -d --build
```

Run the database migrations the first time the containers start.

```bash
sudo docker compose -f docker-compose-supabase-local.yml exec api sh -c "cd app && alembic upgrade head"
```

### Log in to Web UI

Access `http://localhost:<your_port_for_threatconnectome>` to open the Web UI. Click `Sign up` to create a new account.

### Log in to API

Access `http://localhost:<your_port_for_threatconnectome>/api/docs ` to open the API docs. Expand `auth/token Login For Access Token` and click **Try it out**. Fill in the username and password created in the Web UI, copy the `access_token` returned, and paste it into value area of `Authorize` to complete the authentication.

**🎉🎉🎉 Welcome to Threatconnectome 🎉🎉🎉**

### Stopping Threatconnectome

Stop Docker Compose when you are done.

> For local development environment:
>
> ```bash
> sudo docker compose -f docker-compose-supabase-local.yml down
> ```

## For developer

### Set up development environment variables of Web UI

When developing against Supabase, use the Supabase-specific environment template.

```bash
cd ./web
cp .env.supabase.local .env
vi .env
```

If you want to run it, please type the following command

```bash
cd ./web
npm run start  # to check operation and launch the webpage when developing Web UI
```

## :wrench: Troubleshooting

### Unable to log in via Web UI

Confirm that the API container is running. Execute `sudo docker compose -f docker-compose-supabase-local.yml ps` or check `http://localhost:<your_port_for_threatconnectome>/api/docs`.

### Container restarting or unhealthy

Add the container name to the logs command to focus on the failing service. For example, when the API container is restarting:

```bash
sudo docker compose -f docker-compose-supabase-local.yml logs api  # use -f to follow output
```

### Unable to successfully build Web UI

Dependency installation may have failed. Remove `./web/node_modules` and reinstall.

## :test_tube: Testing

### test api

Run the Supabase-aware API tests.

```bash
sh testapi_supabase.sh
```

`docker-compose-supabase-test.yml` contains the Supabase test configuration.

## Docker container

Docker containers in `docker-compose-supabase-local.yml`
| Container name | Description |
| --------------- | ------------------------- |
| supabase-auth | Authentication server |
| supabase-db | PostgreSQL database |
| supabase-studio | Dashboard |
| supabase-kong | API gateway |
| supabase-meta | PostgreSQL API server |

## Top directory structure

| Name     | Description                                                      | Docker container to mount |
| -------- | ---------------------------------------------------------------- | ------------------------- |
| .github  | workflow file for github actions, template file for pull request | -                         |
| .vscode  | vscode settings(format specification, extended functions)        | -                         |
| api      | api server created with fastapi                                  | api                       |
| e2etests | e2e test                                                         | e2etests                  |
| firebase | emulator of firebase authentication                              | firebase                  |
| key      | credential key to use in the API                                 | api                       |
| nginx    | nginx configuration directory                                    | web                       |
| scripts  | storing scripts that run outside of the server                   | -                         |
| traefik  | reverse proxy                                                    | traefik                   |
| web      | frontend built with React.js                                     | web (only web/build)      |
