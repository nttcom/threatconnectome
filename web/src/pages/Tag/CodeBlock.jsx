import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { Box, IconButton, Paper, Tooltip, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

export function CodeBlock(props) {
  const { visible = true } = props;
  const [tooltipTitle, setTooltipTitle] = useState("Copy");
  const handleCloseTip = () => {
    setTooltipTitle("Copy");
  };
  const handleClickButton = () => {
    setTooltipTitle("Copied!");
  };
  const commandText = "pip install -U XXXXX";
  if (!visible) return null;

  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="h6" gutterBottom visible={false}>
        Install
      </Typography>
      <Paper
        variant="outlined"
        sx={{
          px: 3,
          py: 2,
          bgcolor: "grey.800",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Typography>{commandText}</Typography>
        <Tooltip arrow onClose={handleCloseTip} title={tooltipTitle}>
          <IconButton
            onClick={() => {
              handleClickButton();
              navigator.clipboard.writeText(commandText);
            }}
          >
            <ContentCopyIcon sx={{ color: "white" }} />
          </IconButton>
        </Tooltip>
      </Paper>
    </Box>
  );
}
CodeBlock.propTypes = {
  visible: PropTypes.bool,
};
