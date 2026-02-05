import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useApplyPTeamInvitationMutation, useGetPTeamInvitationQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { commonButtonStyle } from "../../utils/const";
import { errorToString } from "../../utils/func";

export function AcceptPTeamInvitation() {
  const { t } = useTranslation("acceptPTeamInvitation", {
    keyPrefix: "AcceptPTeamInvitationPage",
  });
  const { enqueueSnackbar } = useSnackbar();

  const [applyPTeamInvitation] = useApplyPTeamInvitationMutation();

  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const tokenId = params.get("token");

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: detail,
    error: detailError,
    isLoading: detailIsLoading,
  } = useGetPTeamInvitationQuery({ path: { invitation_id: tokenId } }, { skip });

  if (skip) return <></>;
  if (detailError)
    throw new APIError(t("invalidInvitation"), {
      api: "getPTeamInvitation",
    });
  if (detailIsLoading) return <>{t("loadingUserInfo")}</>;

  const handleAccept = async (event) => {
    event.preventDefault();
    async function onSuccess(success) {
      enqueueSnackbar(t("nowMember", { pteamName: detail.pteam_name }), { variant: "info" });
      params.delete("token");
      params.set("pteamId", detail.pteam_id);
      navigate("/pteam?" + params.toString());
    }
    function onError(error) {
      enqueueSnackbar(t("acceptFailed", { error: errorToString(error) }), { variant: "error" });
    }
    await applyPTeamInvitation({ body: { invitation_id: tokenId } })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Typography variant="h6">{t("title")}</Typography>
      <Typography>
        {t("teamName")}: {detail.pteam_name}
      </Typography>
      <Typography>
        {t("teamId")}: {detail.pteam_id}
      </Typography>
      <Typography>
        {t("invitationCreatedBy")} {detail.email} ({detail.user_id})
      </Typography>
      <Box display="flex" flexDirection="row">
        <Button onClick={handleAccept} disabled={!detail.pteam_id} sx={commonButtonStyle}>
          {t("accept")}
        </Button>
      </Box>
    </>
  );
}
