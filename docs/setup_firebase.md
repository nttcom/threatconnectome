# Threatconnectome Setup Guide (Firebase)

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
    - The same with `FIREBASE_API_KEY` in ../.env
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

### Run Docker Compose

Start Docker Compose and confirm the services are healthy.

```bash
cd ..
sudo docker compose -f docker-compose-firebase-local.yml up -d --build
```

Run the database migrations the first time the containers start.

```bash
sudo docker compose -f docker-compose-firebase-local.yml exec api sh -c "cd app && alembic upgrade head"
```

### Log in to Web UI

Access `http://localhost:<your_port_for_threatconnectome>`to see Web UI.
Click `Sign up` to create a new account.

### Log in to API

Access `http://localhost:<your_port_for_threatconnectome>/api/docs ` to see API Documents.
Open `auth/token Login For Access Token` on API page, and click `Try it out` on the right.
Fill in username and password created at Web UI, copy `access_token` in Response Body, and paste it into value area of `Authorize` to complete the authentication.

**🎉🎉🎉Welcome to Threatconnectome🎉🎉🎉**

### Stopping Threatconnectome

Stop Docker Compose from running.

> For local development environment:
>
> ```bash
> sudo docker compose -f docker-compose-firebase-local.yml down
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
npm run start  # to check operation and launch the webpage when developing Web UI
```

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
| web      | frontend built with React.js                                     | web (only web/build directory) |
