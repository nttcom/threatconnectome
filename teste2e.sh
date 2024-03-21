docker compose -f docker-compose-e2e.yml build
docker compose -f docker-compose-e2e.yml run --rm api sh -c "cd app && alembic upgrade head"
docker compose -f docker-compose-e2e.yml run --rm e2eclient pytest -vv -s e2etests/test_e2e.py
docker compose -f docker-compose-e2e.yml down -v
