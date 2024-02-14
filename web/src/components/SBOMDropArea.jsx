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
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useRef, useState } from "react";

import { WaitingModal } from "../components/WaitingModal";
import { uploadSBOMFile } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";
import { errorToString } from "../utils/func";

function PreUploadModal(props) {
  const { sbomFile, open, onSetOpen, onCompleted } = props;
  const [groupName, setGroupName] = useState("");

  const handleClose = () => {
    setGroupName("");
    onSetOpen(false);
  };
  const handleUpload = () => {
    onCompleted(groupName); // parent will close me
    setGroupName(""); // reset for next open
  };

  return (
    <Dialog fullWidth open={open} onClose={handleClose}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} variant="inherit">
            Upload SBOM File
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box display="flex" flexDirection="column">
          <TextField
            label="Group name"
            size="small"
            value={groupName}
            onChange={(event) => setGroupName(event.target.value)}
            required
            error={!groupName}
            sx={{ mt: 2 }}
          />
          <Box display="flex" flexDirection="row" sx={{ mt: 1, ml: 1 }}>
            <Typography sx={{ fontWeight: "bold" }}>Selected file: </Typography>
            <Typography>{sbomFile?.name}</Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Box sx={{ display: "flex", flexDirection: "row", mr: 1, mb: 1 }}>
          <Box sx={{ flex: "1 1 auto" }} />
          <Button onClick={handleUpload} disabled={!groupName} sx={modalCommonButtonStyle}>
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

  useEffect(() => {
    dropRef.current.addEventListener("dragover", handleDragOver);
    dropRef.current.addEventListener("drop", handleDrop);
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
  const handlePreUploadCompleted = (group) => {
    setPreModalOpen(false);
    processUploadSBOM(sbomFile, group);
  };

  const processUploadSBOM = (file, group) => {
    if (!file || !group) {
      alert("Something went wrong: missing file or group.");
      return;
    }
    setIsOpenWaitingModal(true);
    enqueueSnackbar(`Uploading SBOM file: ${file.name}`, { variant: "info" });
    uploadSBOMFile(pteamId, group, file)
      .then((response) => {
        enqueueSnackbar("Upload SBOM succeeded", { variant: "success" });
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
        onCompleted={(group) => handlePreUploadCompleted(group)}
      />
      <WaitingModal isOpen={isOpenWaitingModal} text="Uploading SBOM file" />
    </>
  );
}
SBOMDropArea.propTypes = {
  pteamId: PropTypes.string.isRequired,
  onUploaded: PropTypes.func.isRequired,
};
