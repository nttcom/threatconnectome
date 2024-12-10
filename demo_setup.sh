#! /bin/bash -l

force_mode=0;
docker_yml="docker-compose-demo.yml";

function usage() {
    cat >&2 <<EOD
Usage: $0 [-f]
Options:
    -f: force overwrite exist files
    -h: show this message and exit
EOD
    exit 255;
}

function abort_because_already_configured() {
    cat >&2 <<EOD
It seems like this directory is already configured.
Give -f option to force override existing files.
aborting...
EOD
    exit 254;
}

concealed_key="-----BEG_IN RSA P_RIVATE K_EY-----\_nMIIEpAI_BAAKCAQE_A1hes3Ab_HfSgB8Wz_Ryj0n57T_bTsODUbh_ii0tS7JV_X/JIFSmt_4MuvstVN_6Yj15xpi_NxkVlGOU_gv08bNXN_tmkXAB0H_IbFvgNcz_dHSsg2Lt_CbW4c8p4_xshnltd0_/hSlax/x_QRPMbk07_POc9GOFl_IA+kg1wk_B6QlTvXU_oIxnTbqu_f9jBtC3q_HXACmNVw_oeeZXm8S_AHzPHkLe_20mt/aU/_hqKT5rqL_lTBikJFm_Ssr1nhrc_tVnUQ/rI_8t/w0+PF_rN3RDOG8_0lySpQC8_f/Pnvv6y_3lEsAwI2_l1Hl6AoM_WCjHKCXj_/VxFUU0U_EacBM/x7_esA5A0sa_BzaQPtDo_3SsZvmmi_VViSjHQI_DAQABAoI_BAGJ3VRu_FSq73fZ1_KTVrUscv_R1KPvLDC_juz8Rj7w_cG/GgPyq_xLwFMnPv_wvvL8D0w_V0e8E77B_5gYw7l+o_HgrtXpTA_xQzsDLqX_P6UqHEX5_c8fpekJX_NyFF/s7T_nY1WdZZF_hLJHpth8_UOh7+g+9_asNKLoH0_GOYiyr38_NqT4rnKD_j8phJaXb_FczMRwp0_8K7UYJSu_SEsP9Sak_6HZwp3QC_0QM3W+H3_rvY/58tN_p+QHR4HC_XzzUP2nI_KOLCLjaU_Q8cJOAVf_12KdN5+E_Vjbij2bD_h+sUIrEL_+7WuDEF8_Ei4kYXoL_ode8NXgw_Gjn+DbCK_2M6ASx1U_At1qOdRW_RhbZljMW_On9YtDcE_CgYEA/XG_8xXLhEGR_qUvA3R8E_betUr+8s_5JPvUG6v_vmgdpO0K_wjsDaNSO_mz6oTZaU_wrbXGOmP_e/Dis20s_VpPJnbPB_+gHIvbO9_pxWAhjkG_XbRdTNmE_npD7GcnY_iwP9PVmP_38hQEXbZ_hXV8qEtQ_DYd7v22Y_G5NenXiN_rNCr8KZR_jhyiPKSk_CgYEA2EB_aDF+/T0w_5bFkfES5_1vHxK1/9_ImOKa6bB_JN3VGW4D_JbCt6vrm_E4N0NhxV_Qe+IfPZf_qNg+slhg_RkB+3YdL_PUgn2R1k_iComr377_FCKhjuiu_qSZX3jZY_VrEDIZe2_AKU904D9_Bf0aiSlr_rvH78mTw_Zc1EWBe+_r+cPzoAq_TwxvkxNU_CgYEAnPc_tL6h3hZx_7UUSfKBy_MNWYDKJ3_zlVk2Q7E_X4vCGFwK_1sKP2QQU_EkgbGnqR_RYrR6wb0_K5HEBdYu_qKw9KSOk_ln82YW8J_nYqun/J/_Y9eKFUd+_YGpwacde_CrL8y1tF_xRYdqMNP_8t0RyHVk_bgyj8qog_k6uQ5Lw+_GnLemluX_lQlc3Wwk_CgYEApSp_pXIAYtzE_pvqZHAzF_v/TkVVOo_HAbY5yXi_6QyBQT30_K2pJO2rM_JWVGcjmr_qIORxJfM_MkKPiFnV_lnKWMw6t_ma2tubco_XJONHocm_r5dPu73e_ARVnETKC_wBvMn3Cn_MtECarNf_DZ7mEJLR_SzpJSzZr_IeXoaDwi_iWk6emcL_aXq/ER80_CgYAvGPg_V0SGce/s_JgDQDxbl_4oRPgWjB_hmhYC6kS_vZjXuKNb_0WY3Sc4a_Ct4+IU1G_JiMv/2Hc_10ybXgsz_DyfbwYsL_oJ3fbrRj_yLsuoExN_GnWt0BPh_trRuu/e/_1EiOibnm_3DxDBlGy_Y4iIkWCa_/C7TgWhf_BKvG3gRW_Q9r+bicM_SdpnmmA=_=\n-----_END RSA _PRIVATE _KEY-----_";

function gen_fake_firebase_credential() {
    output_file=$1;
    cat > "${output_file}" <<EOD
{
  "type": "service_account",
  "project_id": "demo-project",
  "private_key_id": "0000000000000000000000000000000000000000",
  "private_key": "${concealed_key//_/}",
  "client_email": "fake@localhost.localdomain",
  "client_id": "000000000000000000000",
  "auth_uri": "fake_uri",
  "token_uri": "fake_uri",
  "auth_provider_x509_cert_url": "fake_url",
  "client_x509_cert_url": "fake_url"
}
EOD
}

while getopts "fh" OPT; do
    case "${OPT}" in
        f) force_mode=1;;
        *) usage;;
    esac
done;

declare -A override_files=(
    ["firebase/.firebaserc"]="firebase/.firebaserc.for_demo"
    ["firebase/data/auth_export/accounts.json"]="firebase/data-demo/auth_export/accounts.json"
    ["firebase/data/auth_export/config.json"]="firebase/data-demo/auth_export/config.json"
    ["firebase/data/firebase-export-metadata.json"]="firebase/data-demo/firebase-export-metadata.json"
    [".env"]=".env.for_demo"
    ["web/.env"]="web/.env.for_demo"
);

# shellcheck disable=SC1091
. .env.for_demo || exit 253;
firebase_credential_filepath="${FIREBASE_CRED#/}";
auto_generate_files=(
    "data"
    "${firebase_credential_filepath}"
);

if [ ${force_mode} -ne 1 ]; then
    # check before generate files
    for item in "${auto_generate_files[@]}"; do
        [ -e "${item}" ] && abort_because_already_configured;
    done;

    # check before override files
    for copy_to in "${!override_files[@]}"; do
        copy_from="${override_files["${copy_to}"]}";
        if [ -f "${copy_to}" ]; then
            # compare mtime & filesize
            stat_from=$(stat -c %Y%s "${copy_from}");
            stat_to=$(stat -c %Y%s "${copy_to}");
            [ "${stat_from}" != "${stat_to}" ] && abort_because_already_configured;
        fi
    done;
fi

# generate files
gen_fake_firebase_credential "${firebase_credential_filepath}" || exit 10;

# create/override files
for copy_to in "${!override_files[@]}"; do
    to_dir=$(dirname "${copy_to}");
    if [ ! -d "${to_dir}" ]; then
        mkdir -p "${to_dir}" || exit 20;
    fi
    copy_from="${override_files["${copy_to}"]}";
    cp -pfT "${copy_from}" "${copy_to}" || exit 30;
done;

# build docker image
echo "building docker images,";
echo "this process should take several minutes. please wait for a while...";
docker compose -f "${docker_yml}" build || exit 40;

# insert demo topics
echo "importing sample data.";
docker compose -f "${docker_yml}" up -d db || exit 50;
sleep 5
docker compose -f "${docker_yml}" cp set_up_demo_environment/demo_data db:/ || exit 60;
docker compose -f "${docker_yml}" exec -T db pg_restore --clean --if-exists -U postgres -d postgres demo_data || exit 70;
docker compose -f "${docker_yml}" down -v || exit 80;

# done!
echo;
echo "setup completed.";
echo "run 'demo_launch.sh' to start Threatconnectome Demo";
echo "and access to 'http://localhost' with Web browser";
echo;
echo "see README.md for demo accounts and contents.";
