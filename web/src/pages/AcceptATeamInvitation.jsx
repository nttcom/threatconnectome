import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { getUser } from "../slices/user";
import { getATeamInvited, applyATeamInvitation } from "../utils/api";
import { commonButtonStyle } from "../utils/const";

export default function AcceptATeamInvitation() {
  const [detail, setDetail] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const tokenId = params.get("token");

  useEffect(() => {
    getATeamInvited(tokenId)
      .then((response) => setDetail(response.data))
      .catch((error) => {
        setErrorMessage(<Typography>This invitation is invalid or already expired.</Typography>);
      });
  }, [tokenId]);

  const handleAccept = async (event) => {
    event.preventDefault();
    async function onSuccess(success) {
      await dispatch(getUser());
      enqueueSnackbar(`Now you are a member of '${detail.ateam_name}'`, { variant: "info" });
      params.delete("token");
      params.set("ateamId", detail.ateam_id);
      navigate("/ateam?" + params.toString());
    }
    function onError(error) {
      enqueueSnackbar(`Accepting invitation failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    await applyATeamInvitation(tokenId)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return detail.ateam_id ? (
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
  ) : (
    <>{errorMessage}</>
  );
}
