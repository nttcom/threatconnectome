if [ ! -e "../firebase/data" ];then
    docker compose -f ../docker-compose-local.yml up --build -d
    docker compose -f ../docker-compose-local.yml down
fi
sudo chmod -R o+rwx ../firebase/data
sudo cp ./accounts.json ../firebase/data/auth_export/accounts.json
docker compose -f ../docker-compose-local.yml up --build -d
docker compose -f ../docker-compose-local.yml cp demo_data db:/
docker compose -f ../docker-compose-local.yml exec -T db pg_restore --clean --if-exists -U postgres -d postgres demo_data
sudo docker compose -f docker-compose-local.yml exec api sh -c "cd app && alembic upgrade head"
cd ../web
npm ci && npm run build
docker compose -f ../docker-compose-local.yml restart
