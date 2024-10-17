# Demo environment set up

Purpose: This is the procedure to reproduce the environment of the [demo environment](https://demo.threatconnectome.metemcyber.ntt.com/) in your local environment.

## :bangbang: Requirements

Read [README](https://github.com/nttcom/threatconnectome?tab=readme-ov-file#threatconnectome) and
complete until setting up the [Firebase authentication emulator](https://github.com/nttcom/threatconnectome?tab=readme-ov-file#firebase-authentication-emulator).

## :warning: Warning

If you are already using a local environment, be sure to back up your database and firebase. When you run the shell script to set up the demo environment, your data will be overwritten. existing data will be lost.

## :triangular_flag_on_post: Procedures to reproduce the demo environment in the local environment

1. Execute shell script

Under the set_up_demo_data directory, do the following.

```bash
sh set_up.sh
```

2. Access `http://localhost:8000`

Please access local port 8000.
The account and password required to login are the same as for the [demo environment](https://github.com/nttcom/threatconnectome?tab=readme-ov-file#demo-environment).
