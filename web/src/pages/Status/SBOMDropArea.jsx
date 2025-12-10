import { Close as CloseIcon, UploadFile as UploadFileIcon } from "@mui/icons-material";
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
import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";

import dialogStyle from "../../cssModule/dialog.module.css";
import { useUploadSBOMFileMutation } from "../../services/tcApi";
import { maxServiceNameLengthInHalf } from "../../utils/const";
import { countFullWidthAndHalfWidthCharacters, errorToString } from "../../utils/func";

import { WaitingModal } from "./WaitingModal";

function PreUploadModal(props) {
  const { sbomFile, open, onSetOpen, onCompleted } = props;
  const [serviceName, setServiceName] = useState("");
  const { enqueueSnackbar } = useSnackbar();

  const handleClose = () => {
    setServiceName("");
    onSetOpen(false);
  };
  const handleUpload = () => {
    onCompleted(serviceName); // parent will close me
    setServiceName(""); // reset for next open
  };

  const handleServiceNameSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxServiceNameLengthInHalf) {
      enqueueSnackbar(
        `Too long service name. Max length is ${maxServiceNameLengthInHalf} in half-width or ${Math.floor(maxServiceNameLengthInHalf / 2)} in full-width`,
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
            Upload SBOM File
          </Typography>
          <IconButton onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box display="flex" flexDirection="column">
          <TextField
            label="Service name"
            size="small"
            value={serviceName}
            onChange={(event) => handleServiceNameSetting(event.target.value)}
            required
            placeholder={`Max length is ${maxServiceNameLengthInHalf} in half-width or ${Math.floor(maxServiceNameLengthInHalf / 2)} in full-width`}
            helperText={serviceName ? "" : "This field is required."}
            error={!serviceName}
            sx={{ mt: 2 }}
          />
          <Box display="flex" flexDirection="row" sx={{ mt: 1, ml: 1 }}>
            <Typography sx={{ fontWeight: "bold" }}>Selected file: </Typography>
            <Typography>{sbomFile?.name}</Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions className={dialogStyle.action_area}>
        <Box>
          <Box sx={{ flex: "1 1 auto" }} />
          <Button onClick={handleUpload} disabled={!serviceName} className={dialogStyle.submit_btn}>
            Upload
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
}
PreUploadModal.propTypes = {
  sbomFile: PropTypes.object,
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
  onCompleted: PropTypes.func.isRequired,
};

export function SBOMDropArea(props) {
  const { pteamId, onUploaded } = props;
  const dropRef = useRef(null);
  const { enqueueSnackbar } = useSnackbar();
  const [sbomFile, setSbomFile] = useState(null);
  const [preModalOpen, setPreModalOpen] = useState(false);
  const [isOpenWaitingModal, setIsOpenWaitingModal] = useState(false);

  const [uploadSBOMFile] = useUploadSBOMFileMutation();

  useEffect(() => {
    dropRef.current.addEventListener("dragover", handleDragOver);
    dropRef.current.addEventListener("drop", handleDrop);
  }, []);

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    /* nothing to do */
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    const { files } = event.dataTransfer;
    if (files && files.length) {
      if (files.length > 1) {
        alert("Please drop only 1 file");
        return;
      }
      if (!files[0].name.endsWith(".json")) {
        alert("Only *.json is supported");
        return;
      }
      setSbomFile(files[0]);
      setPreModalOpen(true);
    }
  };
  const handlePreUploadCompleted = (service) => {
    setPreModalOpen(false);
    processUploadSBOM(sbomFile, service);
  };

  const processUploadSBOM = (sbomFile, serviceName) => {
    if (!sbomFile || !serviceName) {
      alert("Something went wrong: missing file or service.");
      return;
    }
    setIsOpenWaitingModal(true);
    enqueueSnackbar(`Uploading SBOM file: ${sbomFile.name}`, { variant: "info" });
    uploadSBOMFile({
      path: { pteam_id: pteamId },
      query: { service: serviceName },
      body: { file: sbomFile },
    })
      .unwrap()
      .then((response) => {
        enqueueSnackbar("SBOM Update Request was accepted. Please reload later", {
          variant: "success",
        });
        onUploaded();
      })
      .catch((error) => {
        const msg = errorToString(error);
        enqueueSnackbar(`Operation failed: ${msg}`, { variant: "error" });
      })
      .finally(() => {
        setSbomFile(null);
        setIsOpenWaitingModal(false);
      });
  };

  if (!pteamId) return <></>;

  return (
    <>
      <Box
        alignItems="center"
        justifyContent="center"
        display="flex"
        flexDirection="column"
        ref={dropRef}
        sx={{ width: "100%", minHeight: "300px", border: "4px dotted #888" }}
      >
        <UploadFileIcon sx={{ fontSize: 50, mb: 3 }} />
        <Typography>Drop SBOM file here</Typography>
      </Box>
      <PreUploadModal
        sbomFile={sbomFile}
        open={preModalOpen}
        onSetOpen={setPreModalOpen}
        onCompleted={(service) => handlePreUploadCompleted(service)}
      />
      <WaitingModal isOpen={isOpenWaitingModal} text="Uploading SBOM file" />
    </>
  );
}
SBOMDropArea.propTypes = {
  pteamId: PropTypes.string.isRequired,
  onUploaded: PropTypes.func.isRequired,
};
