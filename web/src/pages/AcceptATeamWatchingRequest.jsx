import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import {
  useApplyATeamWatchingRequestMutation,
  useGetATeamRequestedQuery,
  useGetPTeamQuery,
} from "../services/tcApi";
import { commonButtonStyle } from "../utils/const";
import { errorToString } from "../utils/func";

export function AcceptATeamWatchingRequest() {
  const { enqueueSnackbar } = useSnackbar();
  const [applyATeamWatchingRequest] = useApplyATeamWatchingRequestMutation();

  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const tokenId = params.get("token");
  const pteamId = useSelector((state) => state.pteam.pteamId);

  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, { skip: skip || !pteamId });
  const {
    data: detail,
    error: ateamRequestedError,
    isLoading: ateamRequestedIsLoading,
  } = useGetATeamRequestedQuery(tokenId, { skip: skip || !tokenId });
  if (skip) return <></>;
  if (pteamError) return <>{`Cannot get PTeam: ${errorToString(pteamError)}`}</>;
  if (pteamIsLoading) return <>Now loading PTeam...</>;
  if (ateamRequestedError) return <>This request is invalid or already expired.</>;
  if (ateamRequestedIsLoading) return <>Now loading ATeamRequested...</>;

  const handleAccept = async (event) => {
    event.preventDefault();
    async function onSuccess(success) {
      enqueueSnackbar(
        `Now pteam '${pteam?.pteam_name}' is watched by ateam '${detail.ateam_name}'`,
        { variant: "info" },
      );
      params.delete("token");
      params.set("pteamId", pteamId);
      navigate("/pteam?" + params.toString());
    }
    function onError(error) {
      enqueueSnackbar(`Accepting watching request failed: ${errorToString(error)}`, {
        variant: "error",
      });
    }
    const data = {
      request_id: tokenId,
      pteam_id: pteamId,
    };
    await applyATeamWatchingRequest(data)
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
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
  );
}
