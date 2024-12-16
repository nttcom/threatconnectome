#! /bin/sh

cd "$(dirname "$0")" || exit 255;

files_to_check=$(cd demo/files.d && find . -type f);
some_file_missing=0;
file_already_exist=0;
for file in ${files_to_check}; do
    case ${file} in
    ./firebase/data/*) # can be owned by root with mode 0700 on linux
        if [ -f "${file}" ]; then
            file_already_exist=1;
        elif [ ! -d "./firebase/data/" ]; then
            some_file_missing=1;
        # else
            # skip checking. maybe exist but not having permission to access.
        fi
        ;;
    *)
        [ -f "${file}" ] && file_already_exist=1 || some_file_missing=1;
        ;;
    esac;
done
if [ ${file_already_exist} -ne 0 ] && [ ${some_file_missing} -ne 0 ]; then
    cat <<EOD | tr -d "\t"
	This directory looks dirty -- some config file exist and some are missing.
	Please remove (or fix yourself) all files below and try again.

	${files_to_check}

EOD
    exit 10;
fi

if [ ${file_already_exist} -eq 0 ]; then
    if [ -d data ]; then
        cat <<EOD | tr -d "\t"
	You already have DB data, but this script cannot fix it.
	Please remove ./data directory and try atain.
EOD
        exit 20;
    fi

    (cd demo/files.d && tar cf - .) | tar xf - || exit 30;
    demo/print_fake_firebase_cred.sh > ./key/firebase_credentials.json || exit 40;
fi

docker compose -f docker-compose-demo.yml up -d --build || exit 100;

cat <<EOD | tr -d "\t"

	launched Threatconnectome Demo.
	access to http://localhost with Web browser.

	see README.md for Demo environment (accounts and contents).
EOD
