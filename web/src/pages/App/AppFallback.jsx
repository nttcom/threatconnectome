import { Box, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { APIError } from "../../utils/APIError";

export function AppFallback({ error }) {
  console.log(error);
  return (
    <Box>
      <Typography>Error occurred: {error.message}</Typography>
      {error instanceof APIError && <Typography>called API: {error.api || "unknown"}</Typography>}
    </Box>
  );
}
AppFallback.propTypes = {
  error: PropTypes.object.isRequired,
};
