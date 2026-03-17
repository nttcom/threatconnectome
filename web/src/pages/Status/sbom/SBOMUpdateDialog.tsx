import { Close as CloseIcon, LockOutlined as LockIcon } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { FileDropZone } from "../FileDropZone";
import { useUploadSBOMFileMutation } from "../../../services/tcApi";
import { calculateEstimateTimeFromSize } from "../../../utils/estimator";
import { errorToString } from "../../../utils/func";

import { WaitingModal } from "../WaitingModal";

type Props = {
  open: boolean;
  onClose: () => void;
  pteamId: string;
  serviceName: string;
};

export function SBOMUpdateDialog({ open, onClose, pteamId, serviceName }: Props) {
  const { t } = useTranslation("status", { keyPrefix: "SBOMUpdateDialog" });
  const { enqueueSnackbar } = useSnackbar();

  const [sbomFile, setSbomFile] = useState<File | null>(null);
  const [isOpenWaitingModal, setIsOpenWaitingModal] = useState(false);

  const [uploadSBOMFile] = useUploadSBOMFileMutation();

  const estimateTime = calculateEstimateTimeFromSize(sbomFile?.size ?? 0);

  const handleUpload = () => {
    if (!sbomFile || !serviceName) {
      alert(t("alertMissingFile"));
      return;
    }
    onClose();
    setIsOpenWaitingModal(true);
    enqueueSnackbar(t("uploadingFile", { fileName: sbomFile.name }), { variant: "info" });
    uploadSBOMFile({
      path: { pteam_id: pteamId },
      query: { service: serviceName },
      body: { file: sbomFile },
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar(t("uploadSuccess"), {
          variant: "success",
        });
        setSbomFile(null);
      })
      .catch((error) => {
        const msg = errorToString(error);
        enqueueSnackbar(t("uploadFailed", { message: msg }), { variant: "error" });
      })
      .finally(() => {
        setIsOpenWaitingModal(false);
      });
  };

  const handleDialogClose = () => {
    setSbomFile(null);
    onClose();
  };

  return (
    <>
      <Dialog fullWidth open={open} onClose={handleDialogClose}>
        <DialogTitle>
          <Box sx={{ alignItems: "center", display: "flex", flexDirection: "row" }}>
            <Typography variant="h6" flexGrow={1}>
              {t("updateSBOM")}
            </Typography>
            <IconButton onClick={handleDialogClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
            <TextField
              label={t("serviceName")}
              size="small"
              value={serviceName}
              disabled
              slotProps={{
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <LockIcon fontSize="small" />
                    </InputAdornment>
                  ),
                },
              }}
            />
            <Alert severity="warning" sx={{ fontWeight: "medium" }}>
              {t("sbomWarning")}
            </Alert>
            <FileDropZone
              onFileSelected={setSbomFile}
              selectedFile={sbomFile}
              allowClick={true}
              showFileName={true}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          {/* Display estimated time if a file is selected */}
          {sbomFile && (
            <Box
              display="flex"
              flexDirection="row"
              gap={1}
              sx={{ flexGrow: 1, alignItems: "center" }}
            >
              <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                {t("estimatedTime")}
              </Typography>
              <Typography variant="body2">{estimateTime}</Typography>
            </Box>
          )}
          <Button variant="contained" onClick={handleUpload} disabled={!sbomFile}>
            {t("upload")}
          </Button>
        </DialogActions>
      </Dialog>
      <WaitingModal isOpen={isOpenWaitingModal} text={t("uploadingSBOMFile")} />
    </>
  );
}
