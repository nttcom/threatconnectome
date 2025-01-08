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

import dialogStyle from "../../cssModule/dialog.module.css";
import { useUpdatePTeamMemberMutation } from "../../services/tcApi";
import { errorToString } from "../../utils/func";

function AdminCheckbox(props) {
  const { checked, editable, modified, onChange } = props;

  return (
    <>
      <Box display="flex" flexDirection="row" alignItems="center" width="40px">
        <Checkbox
          checked={checked}
          disabled={!editable}
          onChange={editable ? onChange : undefined}
          fontSize="small"
        />
        {modified && "*"}
      </Box>
    </>
  );
}

AdminCheckbox.propTypes = {
  checked: PropTypes.bool.isRequired,
  editable: PropTypes.bool.isRequired,
  modified: PropTypes.bool.isRequired,
  onChange: PropTypes.func.isRequired,
};

function UpdateAuthButton(props) {
  const { disabled, onUpdate } = props;

  return (
    <Button disabled={disabled} onClick={onUpdate} className={dialogStyle.submit_btn}>
      Update
    </Button>
  );
}

UpdateAuthButton.propTypes = {
  disabled: PropTypes.bool.isRequired,
  onUpdate: PropTypes.func.isRequired,
};

export function PTeamAuthEditor(props) {
  const { pteamId, memberUserId, userEmail, isTargetMemberAdmin, isCurrentUserAdmin, onClose } =
    props;

  const [checked, setChecked] = useState(isTargetMemberAdmin);

  const [updatePTeamMember] = useUpdatePTeamMemberMutation();

  const { enqueueSnackbar } = useSnackbar();

  const handleCheckedChange = (event) => {
    setChecked(event.target.checked);
  };

  const handleSave = async () => {
    function onSuccess(success) {
      enqueueSnackbar("Update pteam authority succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Update pteam authority failed: ${errorToString(error)}`, {
        variant: "error",
      });
    }

    const data = { is_admin: checked };

    await updatePTeamMember({ pteamId, userId: memberUserId, data })
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
                <AdminCheckbox
                  checked={checked}
                  editable={isCurrentUserAdmin}
                  modified={isTargetMemberAdmin !== checked}
                  onChange={handleCheckedChange}
                />
              </TableCell>
              <TableCell>Role</TableCell>
              <TableCell>To administrate the pteam.</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <UpdateAuthButton disabled={isTargetMemberAdmin === checked} onUpdate={handleSave} />
      </Box>
    </>
  );
}

PTeamAuthEditor.propTypes = {
  pteamId: PropTypes.string.isRequired,
  memberUserId: PropTypes.string,
  userEmail: PropTypes.string,
  isTargetMemberAdmin: PropTypes.bool.isRequired,
  isCurrentUserAdmin: PropTypes.bool.isRequired,
  onClose: PropTypes.func,
};
