import { ErrorOutline as ErrorOutlineIcon } from "@mui/icons-material";
import { IconButton, Tooltip } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

export function WarningTooltip(props) {
  const { message } = props;

  return (
    <Tooltip title={message} placement="top">
      <IconButton size="small" color="error">
        <ErrorOutlineIcon fontSize="small" />
      </IconButton>
    </Tooltip>
  );
}

WarningTooltip.propTypes = {
  message: PropTypes.string.isRequired,
};
