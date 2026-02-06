import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import dialogStyle from "../../cssModule/dialog.module.css";
import { useDeletePTeamMemberMutation } from "../../services/tcApi";
import { errorToString } from "../../utils/func";

export function PTeamMemberRemoveModal(props) {
  const { memberUserId, userName, pteamId, pteamName, onClose } = props;
  const { t } = useTranslation("pteam", { keyPrefix: "PTeamMemberRemoveModal" });

  const { enqueueSnackbar } = useSnackbar();

  const [deletePTeamMember] = useDeletePTeamMemberMutation();

  const handleRemove = async () => {
    function onSuccess(success) {
      enqueueSnackbar(t("removeMemberSucceeded"), { variant: "success" });
      if (onClose) onClose();
    }
    function onError(error) {
      enqueueSnackbar(t("removeMemberFailed", { error: errorToString(error) }), {
        variant: "error",
      });
    }
    await deletePTeamMember({ path: { pteam_id: pteamId, user_id: memberUserId } })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <DialogTitle>
        <Box display="flex" flexDirection="row">
          <Typography className={dialogStyle.dialog_title}>{t("confirm")}</Typography>
          <Box flexGrow={1} />
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box display="flex" flexWrap="wrap" alignItems="baseline" sx={{ my: 2 }}>
          <Typography>{t("confirmRemove", { userName, pteamName })}</Typography>
        </Box>
      </DialogContent>
      <DialogActions className={dialogStyle.action_area}>
        <Button onClick={handleRemove} className={dialogStyle.delete_btn}>
          {t("remove")}
        </Button>
      </DialogActions>
    </>
  );
}

PTeamMemberRemoveModal.propTypes = {
  memberUserId: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired,
  pteamId: PropTypes.string.isRequired,
  pteamName: PropTypes.string.isRequired,
  onClose: PropTypes.func,
};
