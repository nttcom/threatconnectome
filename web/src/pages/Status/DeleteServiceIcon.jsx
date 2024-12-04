import { Delete as DeleteIcon, Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Tooltip,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import dialogStyle from "../../cssModule/dialog.module.css";

import { PTeamServiceDelete } from "./PTeamServiceDelete";

export function DeleteServiceIcon(props) {
  const { pteamId } = props;

  const [modalOpen, setModalOpen] = useState(false);

  const handleModalClose = () => {
    setModalOpen(false);
  };

  return (
    <>
      <Tooltip title="Service Delete">
        <IconButton onClick={() => setModalOpen(true)}>
          <DeleteIcon />
        </IconButton>
      </Tooltip>
      <Dialog
        open={modalOpen}
        onClose={handleModalClose}
        maxWidth="md"
        fullWidth
        sx={{ maxHeight: "100vh" }}
      >
        <DialogTitle>
          <Box alignItems="center" display="flex" flexDirection="row">
            <Typography flexGrow={1} className={dialogStyle.dialog_title}>
              Delete Services
            </Typography>
            <IconButton onClick={handleModalClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <PTeamServiceDelete pteamId={pteamId} />
        </DialogContent>
      </Dialog>
    </>
  );
}
DeleteServiceIcon.propTypes = {
  pteamId: PropTypes.string.isRequired,
};
