import CloseIcon from "@mui/icons-material/Close";
import { Box, DialogTitle, IconButton } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

export function DialogHeader({ title, onClose }) {
  return (
    <Box sx={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", px: 2 }}>
      <DialogTitle sx={{ gridColumn: 2, justifySelf: "center" }}>{title}</DialogTitle>
      <Box sx={{ gridColumn: 3, justifySelf: "end", display: "flex", alignItems: "center" }}>
        <IconButton onClick={onClose} aria-label="Close dialog">
          <CloseIcon />
        </IconButton>
      </Box>
    </Box>
  );
}

DialogHeader.propTypes = {
  title: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
};
