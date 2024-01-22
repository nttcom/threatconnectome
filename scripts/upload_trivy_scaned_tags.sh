#! /bin/bash -l

# constants: edit below to modify
api_endpoint="http://localhost/tcapi"
trivy_command_path="/usr/bin/trivy"
trivy_timeout="360m"  # give enough time to scan your target path

# variables: specify by options, environment variable or hardcode below
# priority - 1: option args, 2: environment variables, 3: defined values
scan_path=${THREATCONNECTOME_SCAN_PATH:-""}  # e.g. /, /usr/src/metemcyber
refresh_token=${THREATCONNECTOME_REFRESH_TOKEN:-""}  # e.g. eyJfQX......MjA3In0=
pteam_id=${THREATCONNECTOME_PTEAM_ID:=""}  # e.g. 070fc9c8-7b53-479b-be24-211543c1eeb9
group=${THREATCONNECTOME_GROUP:-""}  # e.g. "group alpha"
gradual=${THREATCONNECTOME_UPDATE_GRADUAL:-"0"}  # e.g. 0, 1000, 5000


######## DO NOT EDIT BELOW THIS LINE ########

function usage() {
    cat <<EOD >&2
Usage: $0 [-h][-s SCAN_PATH][-r REFRESH][-p PTEAM_ID][-g GROUP][-G GRADUAL]
  -h: Print this message and exit.
  -s: Scan path. default: env[THREATCONNECTOME_SCAN_PATH].
  -r: Refresh token to access api server. default: env[THREATCONNECTOME_REFRESH_TOKEN].
  -p: UUID of the pteam. default: env[THREATCONNECTOME_PTEAM_ID].
  -g: Group name. default: env[THREATCONNECTOME_GROUP].
  -G: Number of gradual update, 0 for not gradual. default: env[THREATCONNECTOME_UPDATE_GRADUAL].
EOD
    exit
}

while getopts "hs:r:p:g:G:" OPT; do
    case "$OPT" in
        s) scan_path="${OPTARG}";;
        r) refresh_token="${OPTARG}";;
        p) pteam_id="${OPTARG}";;
        g) group="${OPTARG}";;
        G) gradual="${OPTARG}";;
        *) usage;;
    esac
done
shift $((${OPTIND} - 1))

function giveup() {
    echo >&2 "$*"
    exit 255
}

[ -n "${scan_path}" ] || giveup "Missing scan path"
[ -n "${refresh_token}" ] || giveup "Missing refresh token"
[ -n "${pteam_id}" ] || giveup "Missing pteam_id"
[ -n "${group}" ] || giveup "Missing group"
[ -n "${gradual}" ] || giveup "Missing gradual"

trivy_output=$(tempfile) || (echo >&2 "cannot create tempfile"; exit 255)
tags_jsonl=$(tempfile) || (echo >&2 "cannot create tempfile"; exit 255)
trap "rm -f -- '${trivy_output}' '${tags_jsonl}'" EXIT HUP INT QUIT TERM

script_path=`dirname $0`

echo >&2 "processing trivy."
trivy_cmd="${trivy_command_path} fs '${scan_path}' --list-all-pkgs --exit-code 0 --timeout '${trivy_timeout}' -f json -o '${trivy_output}' -q"
echo >&2 "${trivy_cmd}"
eval "${trivy_cmd}" || giveup "trivy scan failed with ret_code=$?."

echo >&2 "processing trivy_tags."
trivy_tags_cmd="python3 ${script_path}/trivy_tags.py -i '${trivy_output}' -o '${tags_jsonl}'"
echo >&2 "${trivy_tags_cmd}"
eval "${trivy_tags_cmd}" || giveup "trivy_tags failed."

echo >&2 "processing upload_tags_file."
upload_tags_cmd="python3 ${script_path}/upload_tags_file.py -e '${api_endpoint}' -i '${tags_jsonl}' -g '${gradual}' '${pteam_id}' '${group}'"
export THREATCONNECTOME_REFRESH_TOKEN="${refresh_token}"  # aboid -r option not to show token on procs
echo >&2 "${upload_tags_cmd}"
eval "${upload_tags_cmd}" || giveup "upload_tags_file failed."

echo >&2 "succeeded!"
