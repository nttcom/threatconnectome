import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { Box, IconButton, Paper, Tooltip, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export function CodeBlock(props) {
  const { visible = true } = props;
  const { t } = useTranslation("package", { keyPrefix: "CodeBlock" });
  const [tooltipTitle, setTooltipTitle] = useState(t("copy"));
  const handleCloseTip = () => {
    setTooltipTitle(t("copy"));
  };
  const handleClickButton = () => {
    setTooltipTitle(t("copySuccess"));
  };
  const commandText = "pip install -U XXXXX";
  if (!visible) return null;

  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="h6" gutterBottom visible={false}>
        {t("install")}
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
