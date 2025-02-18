#!/bin/sh
tar -jxvf ./volumes/db/data-test.tar.bz2 -C ./volumes/db/
docker compose -f docker-compose-test-supabase.yml up --build -d
docker compose -f docker-compose-test-supabase.yml exec testapi pytest -vv app/tests/ # --cov --cov-branch --cov-report=term-missing --cov-config=app/tests/.coveragerc
docker compose -f docker-compose-test-supabase.yml down -v
sudo rm -r ./volumes/db/data-test
