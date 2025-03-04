#!/bin/sh
docker compose -f docker-compose-firebase-test.yml up --build -d
docker compose -f docker-compose-firebase-test.yml exec testapi pytest -vv app/tests/ # --cov --cov-branch --cov-report=term-missing --cov-config=app/tests/.coveragerc
docker compose -f docker-compose-firebase-test.yml down -v
