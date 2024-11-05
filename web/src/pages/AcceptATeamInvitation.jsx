import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useApplyATeamInvitationMutation, useGetATeamInvitedQuery } from "../services/tcApi";
import { commonButtonStyle } from "../utils/const";
import { errorToString } from "../utils/func";

export function AcceptATeamInvitation() {
  const { enqueueSnackbar } = useSnackbar();
  const [applyATeamInvitation] = useApplyATeamInvitationMutation();

  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const tokenId = params.get("token");

  const skipByAuth = useSkipUntilAuthTokenIsReady();
  const skip = skipByAuth || tokenId === undefined;
  const {
    data: detail,
    error: invitationError,
    isLoading: invitationIsLoading,
  } = useGetATeamInvitedQuery(tokenId, { skip });

  if (skip) return <></>;
  if (invitationError) return <>{`Cannot get Members: ${errorToString(invitationError)}`}</>;
  if (invitationIsLoading) return <>Now loading Members...</>;

  const handleAccept = async (event) => {
    event.preventDefault();
    async function onSuccess(success) {
      enqueueSnackbar(`Now you are a member of '${detail.ateam_name}'`, { variant: "info" });
      params.delete("token");
      params.set("ateamId", detail.ateam_id);
      navigate("/ateam?" + params.toString());
    }
    function onError(error) {
      enqueueSnackbar(`Accepting invitation failed: ${errorToString(error)}`, {
        variant: "error",
      });
    }
    await applyATeamInvitation({ invitation_id: tokenId })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Typography variant="h6">Do you accept the invitation to the ateam below?</Typography>
      <Typography>ATeam Name: {detail.ateam_name}</Typography>
      <Typography>ATeam ID: {detail.ateam_id}</Typography>
      <Typography>
        Invitation created by {detail.email} ({detail.user_id})
      </Typography>
      <Box display="flex" flexDirection="row">
        <Button onClick={handleAccept} disabled={!detail.ateam_id} sx={commonButtonStyle}>
          Accept
        </Button>
      </Box>
    </>
  );
}
