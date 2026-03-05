import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { IconButton, Tooltip } from "@mui/material";
import { useState } from "react";

import { SBOMUpdateDialog } from "./SBOMUpdateDialog";

export function SBOMUpdateButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Tooltip title="SBOM を更新">
        <IconButton onClick={() => setOpen(true)}>
          <CloudUploadIcon />
        </IconButton>
      </Tooltip>
      <SBOMUpdateDialog open={open} onClose={() => setOpen(false)} />
    </>
  );
}
