#! /bin/sh

cd "$(dirname "$0")" || exit 255;
cd demo || exit 254;
docker compose -f docker-compose-demo.yml down -v;
