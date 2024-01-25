import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React from "react";

import { commonButtonStyle } from "../utils/const";

export function PTeamAutoClose() {
  const { enqueueSnackbar } = useSnackbar();

  const handleSave = async () => {
    enqueueSnackbar("Auto Close Accepted", { variant: "success" });
  };

  return (
    <Box>
      <Box display="flex" flexDirection="row" alignItems="center">
        <Typography variant="body2" mb={1} mr={2}>
          Close only Alerted tags.
        </Typography>
        <Button onClick={handleSave} sx={{ ...commonButtonStyle, mb: 1 }}>
          Done
        </Button>
      </Box>
    </Box>
  );
}
