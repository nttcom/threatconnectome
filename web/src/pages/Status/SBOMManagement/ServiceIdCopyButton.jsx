import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { IconButton, Tooltip } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export function ServiceIdCopyButton({ serviceId }) {
  const { t } = useTranslation("status", { keyPrefix: "DetailsPanel" });
  const [tooltipText, setTooltipText] = useState(t("copyServiceId"));

  if (!serviceId) return null;

  return (
    <Tooltip
      arrow
      onClose={() => {
        setTooltipText(t("copyServiceId"));
      }}
      title={tooltipText}
    >
      <IconButton
        aria-label={t("copyServiceId")}
        onClick={() => {
          navigator.clipboard.writeText(serviceId);
          setTooltipText(t("copySuccess"));
        }}
        size="small"
        sx={{ color: "primary.main", flexShrink: 0, p: 0.5, "&:hover": { color: "primary.dark" } }}
      >
        <InfoOutlinedIcon sx={{ fontSize: 18 }} />
      </IconButton>
    </Tooltip>
  );
}
