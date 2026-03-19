import { PendingActions as PendingActionsIcon } from "@mui/icons-material";
import { Badge, IconButton, Tooltip } from "@mui/material";
import { useEffect, useState } from "react";
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
  const [prevProgressCount, setPrevProgressCount] = useState<number>(0);

  const {
    data: progressesResponse,
    error: sbomUploadProgressError,
    isLoading: sbomUploadProgressIsLoading,
  } = useGetSbomUploadProgressQuery(
    { pteam_id: pteamId },
    {
      pollingInterval: open ? 10000 : prevProgressCount > 0 ? 10000 : 60000,
    },
  );

  useEffect(() => {
    if (progressesResponse) {
      setPrevProgressCount(progressesResponse.length);
    }
  }, [progressesResponse]);

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
