import { Close as CloseIcon, LockOutlined as LockIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  CircularProgress,
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

import { FileDropZone } from "../../components/FileDropZone";
import { useUploadSBOMFileMutation } from "../../services/tcApi";
import { errorToString } from "../../utils/func";

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
  const [isUploading, setIsUploading] = useState(false);

  const [uploadSBOMFile] = useUploadSBOMFileMutation();

  const handleUpload = () => {
    if (!sbomFile || !serviceName) {
      alert(t("alertMissingFile"));
      return;
    }
    setIsUploading(true);
    enqueueSnackbar(t("uploadingFile", { fileName: sbomFile.name }), { variant: "info" });
    uploadSBOMFile({
      path: { pteam_id: pteamId },
      query: { service: serviceName },
      body: { file: sbomFile },
      url: "/pteams/{pteam_id}/upload_sbom_file",
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar(t("uploadSuccess"), {
          variant: "success",
        });
        setSbomFile(null);
        onClose();
      })
      .catch((error) => {
        const msg = errorToString(error);
        enqueueSnackbar(t("uploadFailed", { message: msg }), { variant: "error" });
      })
      .finally(() => {
        setIsUploading(false);
      });
  };

  const handleDialogClose = () => {
    if (!isUploading) {
      setSbomFile(null);
      onClose();
    }
  };

  return (
    <Dialog fullWidth open={open} onClose={handleDialogClose}>
      <DialogTitle>
        <Box sx={{ alignItems: "center", display: "flex", flexDirection: "row" }}>
          <Typography variant="h6" flexGrow={1}>
            {t("updateSBOM")}
          </Typography>
          <IconButton onClick={handleDialogClose} disabled={isUploading}>
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
          {isUploading ? (
            <Box
              sx={{
                alignItems: "center",
                justifyContent: "center",
                display: "flex",
                flexDirection: "column",
                width: "100%",
                minHeight: "300px",
              }}
            >
              <CircularProgress size={60} sx={{ mb: 2 }} />
              <Typography variant="body2">{t("uploading")}</Typography>
            </Box>
          ) : (
            <FileDropZone
              onFileSelected={setSbomFile}
              selectedFile={sbomFile}
              allowClick={true}
              showFileName={true}
            />
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleUpload} disabled={!sbomFile || isUploading}>
          {t("upload")}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
