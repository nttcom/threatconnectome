#! /bin/sh

cd "$(dirname "$0")" || exit 255;
cd demo || exit 254;

docker compose -f docker-compose-demo.yml up -d --build || exit 253

cat <<EOD

launched Threatconnectome Demo.
access to http://localhost with Web browser.

see README.md for Demo environment (accounts and contents).
EOD
