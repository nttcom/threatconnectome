#! /bin/sh

cd $(dirname $0) || exit 255;
pg_restore --clean --if-exists -d postgres ./demo_data.dump;
