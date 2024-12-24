import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Checkbox,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";

import dialogStyle from "../cssModule/dialog.module.css";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useUpdatePTeamMemberMutation } from "../services/tcApi";
import { errorToString } from "../utils/func";

function PTeamAuthEditorMain(props) {
  // wrap me to make sure currentAuth is ready as initial value for useState
  const { pteamId, userId, userEmail, onClose, isAdmin } = props;

  const [checked, setChecked] = useState(isAdmin);

  const [updatePTeamMember] = useUpdatePTeamMemberMutation();

  const { enqueueSnackbar } = useSnackbar();

  const handleCheckedChange = (event) => {
    setChecked(event.target.checked);
  };

  const handleSave = async (targets) => {
    function onSuccess(success) {
      enqueueSnackbar("Update pteam authority succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Update pteam authority failed: ${errorToString(error)}`, {
        variant: "error",
      });
    }

    const data = { is_admin: checked };

    await updatePTeamMember({ pteamId, userId, data })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Box display="flex" flexDirection="row">
        <Typography className={dialogStyle.dialog_title}>Authority: {userEmail}</Typography>
        <Box flexGrow={1} />
        {onClose && (
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        )}
      </Box>
      <TableContainer>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: "10%", fontWeight: 900 }} align="center">
                User
              </TableCell>
              <TableCell sx={{ width: "30%", fontWeight: 900 }}>Authority</TableCell>
              <TableCell sx={{ fontWeight: 900 }}>Description</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell>
                <Checkbox checked={checked} onChange={handleCheckedChange} fontSize="small" />
              </TableCell>
              <TableCell>Administrator</TableCell>
              <TableCell>To administrate the pteam.</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <Button onClick={handleSave} className={dialogStyle.submit_btn}>
          Update
        </Button>
      </Box>
    </>
  );
}

PTeamAuthEditorMain.propTypes = {
  pteamId: PropTypes.string.isRequired,
  userId: PropTypes.string,
  userEmail: PropTypes.string,
  onClose: PropTypes.func,
  isAdmin: PropTypes.bool.isRequired,
};

export function PTeamAuthEditor(props) {
  const { pteamId, userId, userEmail, isAdmin, onClose } = props;

  const skip = useSkipUntilAuthTokenIsReady() || !pteamId;

  if (skip) return <></>;

  return (
    <PTeamAuthEditorMain
      pteamId={pteamId}
      userId={userId}
      userEmail={userEmail}
      onClose={onClose}
      isAdmin={isAdmin}
    />
  );
}

PTeamAuthEditor.propTypes = {
  pteamId: PropTypes.string.isRequired,
  userId: PropTypes.string,
  userEmail: PropTypes.string,
  isAdmin: PropTypes.bool.isRequired,
  onClose: PropTypes.func,
};
