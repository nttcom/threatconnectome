import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React from "react";
import { useDispatch, useSelector } from "react-redux";

import { getPTeamTagsSummary } from "../slices/pteam";
import { autoClose } from "../utils/api";
import { commonButtonStyle } from "../utils/const";

export function PTeamAutoClose() {
  const dispatch = useDispatch();
  const { enqueueSnackbar } = useSnackbar();

  const pteamId = useSelector((state) => state.pteam.pteamId);

  const handleSave = async () => {
    await autoClose(pteamId)
      .then(() => {
        enqueueSnackbar("Auto Close Accepted", { variant: "success" });
        dispatch(getPTeamTagsSummary(pteamId));
      })
      .catch((error) => {
        const resp = error.response;
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" }
        );
      });
  };

  return (
    <Box sx={{ m: 2 }}>
      <Box display="flex" flexDirection="row" alignItems="center">
        <Typography variant="body2" mb={1} mr={2}>
          Manually check alerts that require a response.
        </Typography>
        <Button variant="contained" onClick={handleSave} sx={{ ...commonButtonStyle, mb: 1 }}>
          Run
        </Button>
      </Box>
    </Box>
  );
}
