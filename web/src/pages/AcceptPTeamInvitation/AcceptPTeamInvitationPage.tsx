import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import type { MouseEvent } from "react";
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
  const invitationId = tokenId ?? "";

  const skip = useSkipUntilAuthUserIsReady() || !tokenId;
  const {
    data: detail,
    error: detailError,
    isLoading: detailIsLoading,
  } = useGetPTeamInvitationQuery({ path: { invitation_id: invitationId } }, { skip });

  if (skip) return <></>;
  if (detailError)
    throw new APIError(t("invalidInvitation"), {
      api: "getPTeamInvitation",
    });
  if (detailIsLoading) return <>{t("loadingUserInfo")}</>;
  if (!detail) return <></>;
  const invitationDetail = detail;

  const handleAccept = async (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    async function onSuccess() {
      enqueueSnackbar(t("nowMember", { pteamName: invitationDetail.pteam_name }), {
        variant: "info",
      });
      params.delete("token");
      params.set("pteamId", invitationDetail.pteam_id);
      navigate("/pteam?" + params.toString());
    }
    function onError(error: unknown) {
      enqueueSnackbar(
        t("acceptFailed", { error: errorToString(error as Parameters<typeof errorToString>[0]) }),
        { variant: "error" },
      );
    }
    await applyPTeamInvitation({ body: { invitation_id: invitationId } })
      .unwrap()
      .then(() => onSuccess())
      .catch((error) => onError(error));
  };

  return (
    <>
      <Typography variant="h6">{t("title")}</Typography>
      <Typography>
        {t("teamName")}: {invitationDetail.pteam_name}
      </Typography>
      <Typography>
        {t("teamId")}: {invitationDetail.pteam_id}
      </Typography>
      <Typography>
        {t("invitationCreatedBy")}: {invitationDetail.email} ({invitationDetail.user_id})
      </Typography>
      <Box display="flex" flexDirection="row">
        <Button onClick={handleAccept} disabled={!invitationDetail.pteam_id} sx={commonButtonStyle}>
          {t("accept")}
        </Button>
      </Box>
    </>
  );
}
