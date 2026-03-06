import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { IconButton, Tooltip } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { SBOMUpdateDialog } from "./SBOMUpdateDialog";

type Props = {
  pteamId: string;
  serviceName: string;
};

export function SBOMUpdateButton({ pteamId, serviceName }: Props) {
  const { t } = useTranslation("status", { keyPrefix: "SBOMUpdateButton" });
  const [open, setOpen] = useState(false);

  return (
    <>
      <Tooltip title={t("updateSBOM")}>
        <IconButton onClick={() => setOpen(true)}>
          <CloudUploadIcon />
        </IconButton>
      </Tooltip>
      <SBOMUpdateDialog
        open={open}
        onClose={() => setOpen(false)}
        pteamId={pteamId}
        serviceName={serviceName}
      />
    </>
  );
}

SBOMUpdateButton.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceName: PropTypes.string.isRequired,
};
