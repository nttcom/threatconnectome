#! /bin/sh

docker_yml="docker-compose-demo.yml";

cmd="docker compose -f ${docker_yml} down -v";
echo "${cmd}";
# shellcheck disable=SC2086
exec ${cmd};
