#!/bin/sh
tar -jxvf ./supabase/volumes/db/data-test.tar.bz2 -C ./supabase/volumes/db/
docker compose -f docker-compose-supabase-test.yml up --build -d
docker compose -f docker-compose-supabase-test.yml exec testapi pytest -vv app/tests/ # --cov --cov-branch --cov-report=term-missing --cov-config=app/tests/.coveragerc
docker compose -f docker-compose-supabase-test.yml down -v
sudo rm -r ./supabase/volumes/db/data-test
