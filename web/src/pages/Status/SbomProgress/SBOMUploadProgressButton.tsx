import { PendingActions as PendingActionsIcon } from "@mui/icons-material";
import { Badge, IconButton, Tooltip } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useGetSbomUploadProgressQuery } from "../../../services/tcApi";
// @ts-expect-error TS7016
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";

import { SBOMUploadProgressDialog } from "./SBOMUploadProgressDialog";

type Props = {
  pteamId: string;
};

export function SBOMUploadProgressButton({ pteamId }: Props) {
  const [open, setOpen] = useState(false);
  const { t } = useTranslation("status", { keyPrefix: "SBOMUploadProgressButton" });

  const {
    data: progressesResponse,
    error: sbomUploadProgressError,
    isLoading: sbomUploadProgressIsLoading,
  } = useGetSbomUploadProgressQuery(
    { pteam_id: pteamId },
    {
      skip: !open,
      pollingInterval: 10000,
    },
  );

  if (sbomUploadProgressError)
    throw new APIError(errorToString(sbomUploadProgressError), {
      api: "getSbomUploadProgress",
    });
  if (sbomUploadProgressIsLoading) return <>{t("loadingSbomProgress")}</>;

  const progresses = progressesResponse || [];

  return (
    <>
      <Tooltip title={t("buttonTitle")}>
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
