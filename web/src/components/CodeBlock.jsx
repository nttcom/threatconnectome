import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { IconButton, Paper, Tooltip, Typography } from "@mui/material";
import React, { useState } from "react";

export function CodeBlock() {
  const [tooltipTitle, setTooltipTitle] = useState("Copy");
  const handleCloseTip = () => {
    setTooltipTitle("Copy");
  };
  const handleClickButton = () => {
    setTooltipTitle("Copied!");
  };
  const commandText = "pip install -U XXXXX";

  return (
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
  );
}
