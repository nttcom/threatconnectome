import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
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
import { useState } from "react";

import dialogStyle from "../../cssModule/dialog.module.css";
import { useUpdatePTeamMemberMutation } from "../../services/tcApi";
import { errorToString } from "../../utils/func";

import { AuthAdminCheckbox } from "./AuthAdminCheckbox";
import { UpdateAuthButton } from "./UpdateAuthButton";

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

    await updatePTeamMember({ path: { pteam_id: pteamId, user_id: memberUserId }, body: data })
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
                <AuthAdminCheckbox
                  checked={checked}
                  editable={isCurrentUserAdmin}
                  modified={isTargetMemberAdmin !== checked}
                  onChange={handleCheckedChange}
                />
              </TableCell>
              <TableCell>Administrator</TableCell>
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
  memberUserId: PropTypes.string.isRequired,
  userEmail: PropTypes.string.isRequired,
  isTargetMemberAdmin: PropTypes.bool.isRequired,
  isCurrentUserAdmin: PropTypes.bool.isRequired,
  onClose: PropTypes.func,
};
