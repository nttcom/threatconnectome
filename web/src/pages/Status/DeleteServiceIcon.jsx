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
import { useState } from "react";
import { useTranslation } from "react-i18next";

import dialogStyle from "../../cssModule/dialog.module.css";

import { PTeamServiceDelete } from "./PTeamServiceDelete";

export function DeleteServiceIcon(props) {
  const { pteamId, onServiceDeleted } = props;
  const { t } = useTranslation("status", { keyPrefix: "DeleteServiceIcon" });

  const [modalOpen, setModalOpen] = useState(false);

  const handleModalClose = () => {
    setModalOpen(false);
  };

  const handleServiceDeleted = () => {
    setModalOpen(false);
    if (onServiceDeleted) {
      onServiceDeleted();
    }
  };

  return (
    <>
      <Tooltip title={t("serviceDelete")}>
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
              {t("deleteServices")}
            </Typography>
            <IconButton onClick={handleModalClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <PTeamServiceDelete pteamId={pteamId} onServiceDeleted={handleServiceDeleted} />
        </DialogContent>
      </Dialog>
    </>
  );
}
DeleteServiceIcon.propTypes = {
  pteamId: PropTypes.string.isRequired,
  onServiceDeleted: PropTypes.func,
};
