import { PendingActions as PendingActionsIcon } from "@mui/icons-material";
import { Badge, IconButton, Tooltip } from "@mui/material";
import { useEffect, useState } from "react";

import { useGetSbomUploadProgressQuery } from "../../services/tcApi";
// @ts-expect-error TS7016
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

import { SBOMUploadProgressDialog } from "./SBOMUploadProgressDialog";

type Props = {
  pteamId: string;
};

export function SBOMUploadProgressButton({ pteamId }: Props) {
  const [open, setOpen] = useState(false);

  const {
    data: progressesResponse,
    error: sbomUploadProgressError,
    isLoading: sbomUploadProgressIsLoading,
    refetch: refetchSbomUploadProgress,
  } = useGetSbomUploadProgressQuery({ pteam_id: pteamId });

  if (sbomUploadProgressError)
    throw new APIError(errorToString(sbomUploadProgressError), {
      api: "getSbomUploadProgress",
    });
  if (sbomUploadProgressIsLoading) return <>{"Now loading SbomUploadProgress..."}</>;

  useEffect(() => {
    if (open) refetchSbomUploadProgress();
  }, [open]);

  const progresses = progressesResponse || [];

  return (
    <>
      <Tooltip title="アップロード進捗">
        <IconButton onClick={() => setOpen(true)}>
          <Badge variant="dot" color="primary" invisible={progresses.length === 0}>
            <PendingActionsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <SBOMUploadProgressDialog
        progresses={progresses}
        open={open}
        setOpen={setOpen}
        refetch={refetchSbomUploadProgress}
      />
    </>
  );
}
