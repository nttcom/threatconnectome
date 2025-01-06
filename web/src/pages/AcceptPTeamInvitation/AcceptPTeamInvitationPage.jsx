import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthTokenIsReady } from "../../hooks/auth";
import { useApplyPTeamInvitationMutation, useGetPTeamInvitationQuery } from "../../services/tcApi";
import { commonButtonStyle } from "../../utils/const";
import { errorToString } from "../../utils/func";

export function AcceptPTeamInvitation() {
  const { enqueueSnackbar } = useSnackbar();

  const [applyPTeamInvitation] = useApplyPTeamInvitationMutation();

  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const tokenId = params.get("token");

  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: detail,
    error: detailError,
    isLoading: detailIsLoading,
  } = useGetPTeamInvitationQuery(tokenId, { skip });

  if (skip) return <></>;
  if (detailError) return <>{"This invitation is invalid or already expired."}</>;
  if (detailIsLoading) return <>Now loading user info...</>;

  const handleAccept = async (event) => {
    event.preventDefault();
    async function onSuccess(success) {
      enqueueSnackbar(`Now you are a member of '${detail.pteam_name}'`, { variant: "info" });
      params.delete("token");
      params.set("pteamId", detail.pteam_id);
      navigate("/pteam?" + params.toString());
    }
    function onError(error) {
      enqueueSnackbar(`Accepting invitation failed: ${errorToString(error)}`, { variant: "error" });
    }
    await applyPTeamInvitation({ invitation_id: tokenId })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Typography variant="h6">Do you accept the invitation to the team below?</Typography>
      <Typography>Team Name: {detail.pteam_name}</Typography>
      <Typography>Team ID: {detail.pteam_id}</Typography>
      <Typography>
        Invitation created by {detail.email} ({detail.user_id})
      </Typography>
      <Box display="flex" flexDirection="row">
        <Button onClick={handleAccept} disabled={!detail.pteam_id} sx={commonButtonStyle}>
          Accept
        </Button>
      </Box>
    </>
  );
}
