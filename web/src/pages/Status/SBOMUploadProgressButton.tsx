import { PendingActions as PendingActionsIcon } from "@mui/icons-material";
import { Badge, IconButton, Tooltip } from "@mui/material";
import { useState } from "react";

import { SBOMUploadProgressDialog } from "./SBOMUploadProgressDialog";

export type UploadProgress = {
  serviceName: string;
  progressPercent: number;
  estimatedCompletionTime: string;
};

type Props = {
  progresses: UploadProgress[];
};

export function SBOMUploadProgressButton({ progresses }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Tooltip title="アップロード進捗">
        <IconButton onClick={() => setOpen(true)}>
          <Badge variant="dot" color="primary" invisible={progresses.length === 0}>
            <PendingActionsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <SBOMUploadProgressDialog progresses={progresses} open={open} setOpen={setOpen} />
    </>
  );
}
