import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { IconButton, Tooltip } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export function CopiedIcon(props) {
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

CopiedIcon.propTypes = {
  invitationLink: PropTypes.oneOfType([PropTypes.string, PropTypes.element]).isRequired,
};
