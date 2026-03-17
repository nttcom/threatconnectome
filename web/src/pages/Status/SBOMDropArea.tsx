import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  TextField,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import dialogStyle from "../../cssModule/dialog.module.css";
import { useUploadSBOMFileMutation } from "../../services/tcApi";
import { maxServiceNameLengthInHalf } from "../../utils/const";
import { calculateEstimateTimeFromSize } from "../../utils/estimator";
import { countFullWidthAndHalfWidthCharacters, errorToString } from "../../utils/func";
import { FileDropZone } from "./FileDropZone";

import { WaitingModal } from "./WaitingModal";

interface PreUploadModalProps {
  sbomFile: File | null;
  open: boolean;
  onSetOpen: (open: boolean) => void;
  onCompleted: (serviceName: string) => void;
}

function PreUploadModal(props: PreUploadModalProps) {
  const { t } = useTranslation("status", { keyPrefix: "SBOMDropArea" });
  const { sbomFile, open, onSetOpen, onCompleted } = props;
  const [serviceName, setServiceName] = useState<string>("");
  const { enqueueSnackbar } = useSnackbar();

  const estimateTime = calculateEstimateTimeFromSize(sbomFile?.size ?? 0);

  const handleClose = () => {
    setServiceName("");
    onSetOpen(false);
  };
  const handleUpload = () => {
    onCompleted(serviceName); // parent will close me
    setServiceName(""); // reset for next open
  };

  const handleServiceNameSetting = (string: string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxServiceNameLengthInHalf) {
      enqueueSnackbar(
        t("tooLongServiceName", {
          maxHalf: maxServiceNameLengthInHalf,
          maxFull: Math.floor(maxServiceNameLengthInHalf / 2),
        }),
        {
          variant: "error",
        },
      );
      return;
    }
    setServiceName(string);
  };

  return (
    <Dialog fullWidth open={open} onClose={handleClose}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} className={dialogStyle.dialog_title}>
            {t("uploadSBOMFile")}
          </Typography>
          <IconButton onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box display="flex" flexDirection="column">
          <TextField
            label={t("serviceName")}
            size="small"
            value={serviceName}
            onChange={(event) => handleServiceNameSetting(event.target.value)}
            required
            placeholder={t("maxLengthPlaceholder", {
              maxHalf: maxServiceNameLengthInHalf,
              maxFull: Math.floor(maxServiceNameLengthInHalf / 2),
            })}
            helperText={serviceName ? "" : t("serviceNameRequired")}
            error={!serviceName}
            sx={{ mt: 2 }}
          />
          <Box display="flex" flexDirection="row" sx={{ mt: 1, ml: 1 }}>
            <Typography sx={{ fontWeight: "bold" }}>{t("selectedFile")}</Typography>
            <Typography>{sbomFile?.name}</Typography>
          </Box>
          <Box display="flex" flexDirection="row" sx={{ mt: 1, ml: 1 }}>
            <Typography sx={{ fontWeight: "bold" }}>{t("estimatedTime")}</Typography>
            <Typography>{estimateTime}</Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions className={dialogStyle.action_area}>
        <Box>
          <Box sx={{ flex: "1 1 auto" }} />
          <Button onClick={handleUpload} disabled={!serviceName} className={dialogStyle.submit_btn}>
            {t("upload")}
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
}

interface SBOMDropAreaProps {
  pteamId: string;
  onUploaded: () => void;
}

export function SBOMDropArea(props: SBOMDropAreaProps) {
  const { t } = useTranslation("status", { keyPrefix: "SBOMDropArea" });
  const { pteamId, onUploaded } = props;
  const { enqueueSnackbar } = useSnackbar();
  const [sbomFile, setSbomFile] = useState<File | null>(null);
  const [preModalOpen, setPreModalOpen] = useState<boolean>(false);
  const [isOpenWaitingModal, setIsOpenWaitingModal] = useState<boolean>(false);

  const [uploadSBOMFile] = useUploadSBOMFileMutation();

  const handleFileSelected = (file: File) => {
    setSbomFile(file);
    setPreModalOpen(true);
  };

  const handlePreUploadCompleted = (service: string) => {
    setPreModalOpen(false);
    processUploadSBOM(sbomFile, service);
  };

  const processUploadSBOM = (sbomFile: File | null, serviceName: string) => {
    if (!sbomFile || !serviceName) {
      alert(t("alertMissingFile"));
      return;
    }
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
        onUploaded();
      })
      .catch((error) => {
        const msg = errorToString(error);
        enqueueSnackbar(t("uploadFailed", { message: msg }), { variant: "error" });
      })
      .finally(() => {
        setSbomFile(null);
        setIsOpenWaitingModal(false);
      });
  };

  if (!pteamId) return <></>;

  return (
    <>
      <FileDropZone
        onFileSelected={handleFileSelected}
        selectedFile={null}
        allowClick={false}
        showFileName={false}
      />
      <PreUploadModal
        sbomFile={sbomFile}
        open={preModalOpen}
        onSetOpen={setPreModalOpen}
        onCompleted={(service) => handlePreUploadCompleted(service)}
      />
      <WaitingModal isOpen={isOpenWaitingModal} text={t("uploadingSBOMFile")} />
    </>
  );
}
