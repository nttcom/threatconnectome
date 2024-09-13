#!/bin/sh
docker compose -f docker-compose-test.yml up --build -d
#docker compose -f docker-compose-test.yml exec testapi pytest -s -vv app/tests/integrations/test_ticket_status.py
#docker compose -f docker-compose-test.yml exec testapi pytest -s -vv app/tests/requests/test_pteams.py
#docker compose -f docker-compose-test.yml exec testapi pytest -s -vv app/tests/medium/routers/test_topics.py::test_delete_topic
#docker compose -f docker-compose-test.yml exec testapi pytest -s -vv app/tests/small/test_ssvc_calculator.py
docker compose -f docker-compose-test.yml exec testapi pytest -s -vv app/tests
docker compose -f docker-compose-test.yml down -v
