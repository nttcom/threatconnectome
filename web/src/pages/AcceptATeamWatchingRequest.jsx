import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { getPTeam } from "../slices/pteam";
import { getATeamRequested, applyATeamWatchingRequest } from "../utils/api";
import { commonButtonStyle } from "../utils/const";

export function AcceptATeamWatchingRequest() {
  const [detail, setDetail] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const tokenId = params.get("token");
  const pteamId = useSelector((state) => state.pteam.pteamId);
  const pteam = useSelector((state) => state.pteam.pteam);

  useEffect(() => {
    getATeamRequested(tokenId)
      .then((response) => setDetail(response.data))
      .catch((error) => {
        setErrorMessage(<Typography>This request is invalid or already expired.</Typography>);
      });
  }, [tokenId]);

  useEffect(() => {
    if (!pteamId) return;
    if (!pteam) dispatch(getPTeam(pteamId));
  }, [dispatch, pteamId, pteam]);

  const handleAccept = async (event) => {
    event.preventDefault();
    async function onSuccess(success) {
      enqueueSnackbar(
        `Now pteam '${pteam?.pteam_name}' is watched by ateam '${detail.ateam_name}'`,
        { variant: "info" }
      );
      params.delete("token");
      params.set("pteamId", pteamId);
      navigate("/pteam?" + params.toString());
    }
    function onError(error) {
      enqueueSnackbar(`Accepting watching request failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    const data = {
      request_id: tokenId,
      pteam_id: pteamId,
    };
    await applyATeamWatchingRequest(data)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return detail.ateam_id ? (
    <>
      <Typography variant="h6">
        Does your pteam ({pteam?.pteam_name}) accept the watching request from the ateam below?
      </Typography>
      <Typography>ATeam Name: {detail.ateam_name}</Typography>
      <Typography>ATeam ID: {detail.ateam_id}</Typography>
      <Typography>
        Request created by {detail.email} ({detail.user_id})
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
