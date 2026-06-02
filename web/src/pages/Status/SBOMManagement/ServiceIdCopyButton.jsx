import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { IconButton, Tooltip } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export function ServiceIdCopyButton({ serviceId }) {
  const { t } = useTranslation("status", { keyPrefix: "DetailsPanel" });
  const [tooltipKey, setTooltipKey] = useState("copyServiceId");

  if (!serviceId) return null;

  return (
    <Tooltip
      arrow
      onClose={() => {
        setTooltipKey("copyServiceId");
      }}
      title={t(tooltipKey)}
    >
      <IconButton
        aria-label={t("copyServiceId")}
        onClick={async () => {
          try {
            await navigator.clipboard.writeText(serviceId);
            setTooltipKey("copySuccess");
          } catch {
            setTooltipKey("copyServiceId");
          }
        }}
        size="small"
        sx={{ color: "primary.main", flexShrink: 0, p: 0.5, "&:hover": { color: "primary.dark" } }}
      >
        <InfoOutlinedIcon sx={{ fontSize: 18 }} />
      </IconButton>
    </Tooltip>
  );
}
