#!/bin/sh
cp -r ./volumes/db/data-test-original ./volumes/db/data-test
docker compose -f docker-compose-test-supabase.yml up
docker compose -f docker-compose-test-supabase.yml exec testapi pytest -vv app/tests/ # --cov --cov-branch --cov-report=term-missing --cov-config=app/tests/.coveragerc
docker compose -f docker-compose-test-supabase.yml down -v
sudo rm -r ./volumes/db/data-test
