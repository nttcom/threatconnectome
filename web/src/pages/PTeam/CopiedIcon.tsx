import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { IconButton, Tooltip } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

type CopiedIconProps = {
  invitationLink: string;
};

export function CopiedIcon(props: CopiedIconProps) {
  const { invitationLink } = props;

  const [tooltipOpen, setTooltipOpen] = useState(false);

  const { t } = useTranslation("pteam", { keyPrefix: "CopiedIcon" });

  const handleTooltipOpen = () => {
    setTooltipOpen(true);

    setTimeout(() => {
      setTooltipOpen(false);
    }, 10000);
  };

  const handleClose = () => {
    setTooltipOpen(false);
  };

  return (
    <>
      <IconButton
        onClick={() => {
          navigator.clipboard.writeText(invitationLink);
          handleTooltipOpen();
        }}
      >
        <Tooltip
          title={t("tooltipCopied")}
          placement="top"
          open={tooltipOpen}
          onClose={handleClose}
        >
          <ContentCopyIcon />
        </Tooltip>
      </IconButton>
    </>
  );
}
