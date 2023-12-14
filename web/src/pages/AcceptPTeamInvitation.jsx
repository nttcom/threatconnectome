import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { getUser } from "../slices/user";
import { getPTeamInvited, applyPTeamInvitation } from "../utils/api";
import { commonButtonStyle } from "../utils/const";

export function AcceptPTeamInvitation() {
  const [detail, setDetail] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const tokenId = params.get("token");

  useEffect(() => {
    getPTeamInvited(tokenId)
      .then((response) => setDetail(response.data))
      .catch((error) => {
        setErrorMessage(<Typography>This invitation is invalid or already expired.</Typography>);
      });
  }, [tokenId]);

  const handleAccept = async (event) => {
    event.preventDefault();
    async function onSuccess(success) {
      await dispatch(getUser());
      enqueueSnackbar(`Now you are a member of '${detail.pteam_name}'`, { variant: "info" });
      params.delete("token");
      params.set("pteamId", detail.pteam_id);
      navigate("/pteam?" + params.toString());
    }
    function onError(error) {
      enqueueSnackbar(`Accepting invitation failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    await applyPTeamInvitation(tokenId)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return detail.pteam_id ? (
    <>
      <Typography variant="h6">Do you accept the invitation to the pteam below?</Typography>
      <Typography>PTeam Name: {detail.pteam_name}</Typography>
      <Typography>PTeam ID: {detail.pteam_id}</Typography>
      <Typography>
        Invitation created by {detail.email} ({detail.user_id})
      </Typography>
      <Box display="flex" flexDirection="row">
        <Button onClick={handleAccept} disabled={!detail.pteam_id} sx={commonButtonStyle}>
          Accept
        </Button>
      </Box>
    </>
  ) : (
    <>{errorMessage}</>
  );
}
