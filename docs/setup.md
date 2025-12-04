# Threatconnectome Setup Guide

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

> :house: **Installation for on-premises environment**
>
> Threatconnectome can run in an on-premises environment using Supabase.
> To set up an environment using Supabase, you need to configure environment variables and use a docker-compose-supabase-local.yml
> Therefore, in [Set up environment variables](#set-up-environment-variables), [Set up production environment variables](#set-up-production-environment-variables), and [Run Docker Compose](#run-docker-compose), follow the items marked with :house: instead of the usual setup.

### Set up environment variables

Copy .env.firebase.example, change it to .env and edit the contents

```bash
cp .env.firebase.example .env
vi .env  # change default values
```

:warning: **Values that need to be changed**

- Values that are required when connecting to firebase

  - `FIREBASE_API_KEY`
    - Web API Key in firebase project settings

- Optional values that can be left as it is
  - `DB_USER`
    - Username of DB for connection
  - `DB_PASSWORD`
    - Password to be set for the DB, required when connecting to the DB
  - `SYSTEM_EMAIL`
    - Email address recorded when the system executes an event
    - From email address for sending email with sendgrid
  - `SENDGRID_API_KEY`
    - Api key to send email with sendgrid
  - `VULN_API_KEY`
    - API key for patching vulnerability information in threatconnectome

:warning: **Files that need to be placed**

- Files that are required when connecting to firebase
  - Place the Authentication credential file the path of `FIREBASE_CRED`
    - Refer to [this document](https://firebase.google.com/docs/admin/setup?hl=en#initialize_the_sdk_in_non-google_environments) to download the JSON file that service account private key.

> :house: **Set up environment variables for on-premises environment**
>
> Instead of .env.firebase.example, copy .env.supabase.example, rename it to .env, and edit its contents.
>
> ```bash
> cp .env.supabase.example .env
> vi .env  # change default values
> ```
>
> .env.supabase.example includes additional environment variables required for using Supabase.
>
> - `SUPABASE_POSTGRES_PASSWORD`
>   - Password to be set for the Supabase Postgres
> - `JWT_SECRET`
>   - Secret Json Web Token
> - `ANON_KEY`
> - `SERVICE_ROLE_KEY`
>   - API key of Supabase
> - `DASHBOARD_USERNAME`
>   - Username of Supabase dashboard
> - `DASHBOARD_PASSWORD`
>   - Password to be set for the Supabase dashboard
> - `LOGFLARE_API_KEY`
>   - API key of logflare

### Set up production environment variables

In the default configuration, the test server links to the development API running on `localhost` and the build links to the production API.
To change this so that builds also link to the development environment API, the following must be done in advance.

> ```bash
> cd ./web
> cp .env.firebase.example .env
> vi .env  # set values
> ```

:warning: **Values that need to be changed**

- `VITE_API_BASE_URL`
  - Set it as `http://localhost:<your_port_for_threatconnectome>/api` for local development
- Values can be referred from firebase project setting page

  - `VITE_FIREBASE_API_KEY`
    - The same with `FIREBASE_API_KEY` in ../.envenv
  - `VITE_FIREBASE_APP_ID`
    - App ID
  - Values can be referred from `firebaseConfig` on the page

    - `VITE_FIREBASE_AUTH_DOMAIN`
    - `VITE_FIREBASE_MEASUREMENT_ID`
    - `VITE_FIREBASE_MESSAGING_SENDER_ID`
    - `VITE_FIREBASE_PROJECT_ID`
    - `VITE_FIREBASE_STORAGE_BUCKET`

  - `VITE_FIREBASE_AUTH_SAML_PROVIDER_ID`
    - Set your saml provider id if needed.
  - `VITE_FIREBASE_AUTH_EMULATOR_URL`
    - Set it to `http://localhost:<your_port_for_firebase>`

> :house: **Set up production environment variables for on-premises environment**
>
> Instead of .env.produciton.example, copy .env.supabase.example, rename it to .env.production.local, and edit its contents.
>
> ```bash
> cd ./web
> cp .env.supabase.example .env
> vi .env  # set values
> ```
>
> .env.supabase.example includes additional environment variables required for using Supabase.
>
> - `VITE_AUTH_SERVICE`
> - Authentication service to be used (fixed to suupabase).
> - `VITE_SUPABASE_URL`
>   - URL which the kong container (not auth container) listens to.
> - `VITE_SUPABASE_ANON_KEY`
>   - Same value with ANON_KEY in ../.env.

### Database settings

`docker-compose-prod.yml` is for public environment. Parts that have been commented out, are depending on whether the firebase local emulator is needed to be deplyed or not.
If enabled, it will be the same as `docker-compose-local.yml`, and firebase local emulator will be in use.

- Please use `docker-compose-local.yml` for local development.

### CORS settings (Optional)

Change CORS settings in [main.py](/api/app/main.py), if needed.

### Firebase authentication emulator

You can use the firebase emulator as an authentication platform for testing or running locally.
The `./firebase` directory contains files for the firebase emulator. Place `.firebaserc` of your firebase project directly under this directory.

If you need more information about `.firebaserc` , please refer to the official documents:
https://firebase.google.com/docs/cli/targets

### Web UI

```bash
cd ./web
npm ci
npm run build  # to build what is specified in package.json
```

## :sparkles: Get Started to Threatconnectome

### Run Docker Compose

Start Docker Compose and check that the system is operating normally.

> For local development environmrnt:
>
> ```bash
> cd ..
> sudo docker compose -f docker-compose-firebase-local.yml up -d --build  # to start containers
> ```
>
> And set up database if it is the first time to start.
>
> ```bash
> sudo docker compose -f docker-compose-firebase-local.yml exec api sh -c "cd app && alembic upgrade head"
> ```
>
> :house: **Run Docker Compose for on-premises environment**
>
> In an on-premises environment, use docker-compose-supabase-local.yml instead of docker-compose-local.yml.
>
> - For local development environmrnt:
>
> ```bash
> cd ..
> sudo docker compose -f docker-compose-supabase-local.yml up -d --build  # to start containers
> ```
>
> And set up database if it is the first time to start.
>
> ```bash
> sudo docker compose -f docker-compose-supabase-local.yml exec api sh -c "cd app && alembic upgrade head"
> ```

### Log in to Web UI

Access `http://localhost:<your_port_for_threatconnectome>`to see Web UI.
Click `Sign up` to create a new account.

### Log in to API

Access `http://localhost:<your_port_for_threatconnectome>/api/docs ` to see API Documents.
Open `auth/token Login For Access Token` on API page, and click `Try it out` on the right.
Fill in username and password created at Web UI, copy `access_token` in Response Body, and paste it into value area of `Authorize` to complete the authentication.

**🎉🎉🎉Welcome to Threatconnectome🎉🎉🎉**

## :people_holding_hands: Create a team

In Threatconnectome, if a user doesn't belong to any team, basic operations cannot be operated (tag management, invitation creation etc.).
To create a team, please follow the procedures below:

1. After the authentication mentioned above (Log in to API), access `http://localhost:<your_port_for_threatconnectome>/api/docs#/pteams/create_team_teams_post` or scroll down to `teams` ⇨ `POST /pteams Create Team` on API page.
2. Click `Try it out`.
3. Modify the content in `Request body`, change `team_name` from `string` to `your team name`.
4. Click `Execute`.
5. Information, including your team id and name, will be shown in `Response body` below.

:warning: Attention: Authentication is necessary before the team creation.

### Stop of Threatconnectome

Stop Docker Compose from running.

> For local development environmrnt:
>
> ```bash
> sudo docker compose -f docker-compose-firebase-local.yml down
> ```
>
> :house: **Stop of Threatconnectome for on-premises environment**
> Stop Docker Compose from running in the on-premises environment.
>
> - For local development environmrnt:
>
> ```bash
> sudo docker compose -f docker-compose-supabase-local.yml down
> ```

## :wrench: Troubleshooting

### Unable to log in via Web UI

You need to check the API connection point.
If you are using the API container for the development environment, check that the API container is running properly by running `$ sudo docker compose ps` or by communicating to `http://localhost:<your_port_for_threatconnectome>/api/docs`.

### Troubleshooting with container not running

If certain container is restarting or unhealthy, please add the name of the container after `$ sudo docker compose logs`
For example, if api is restarting, error can be targeted by:

```bash
$ sudo docker compose logs api  # -f option is to follow log output
```

### Unable to successfully build Web UI

Installation of dependent packages may have failed.
Remove `./web/node_modules` directory and try installing again.

## For developer

### Set up development environment variables of Web UI

If you want to define development environment variables, do the following

```bash
cd ./web
cp .env.firebase.example .env
vi .env  # set values
```

If you want to run it, please type the following command

```bash
cd ./web
npm run start  # to check operation and launch the >webpage when developing Web UI
```

> :house: **Set up development environment variables of Web UI for on-premises environment**
>
> In an on-premises environment, use .env.supabase.local instead of .env.firebase.local.

## :test_tube: Testing

### test api

Start Docker containers for test and run api test.

```bash
sh testapi.sh
```

docker-compose-test.yml is the config file for testing.

## Docker container

Docker containers in docker-compose-local.yml
| Container name | Description |
| --------- | --------|
| api | Api server |
| db | Database of postgresSQL |
| traefik | Reverse proxy |
| web | Nginx hosting front-end |
| firebase | emulator of firebase authentication |

> :house: **Docker container for on-premises environment**
>
> In an on-premises environment, the following containers are required for Supabase.
>
> | Container name  | Description               |
> | --------------- | ------------------------- |
> | supabase-auth   | Authentication Server     |
> | supabase-db     | Database of postgresSQL   |
> | supabase-studio | Dashboard                 |
> | supabase-kong   | Api Gateway               |
> | supabase-meta   | Api server of postgresSQL |

## Top directory structure

| Name     | Description                                                      | Docker container to mount      |
| -------- | ---------------------------------------------------------------- | ------------------------------ |
| .github  | workflow file for github actions, template file for pull request | -                              |
| .vscode  | vscode settings(format specification, extended functions)        | -                              |
| api      | api server created with fastapi                                  | api                            |
| e2etests | e2e test                                                         | e2etests                       |
| firebase | emulator of firebase authentication                              | firebase                       |
| key      | credential key to use in the API                                 | api                            |
| nginx    | nginx configuration directory                                    | web                            |
| scripts  | storing scripts that run outside of the server                   | -                              |
| traefik  | reverse proxy                                                    | traefik                        |
| web      | front end created with React.js                                  | web (only web/bulid directory) |
