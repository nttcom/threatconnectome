import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  TextField,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useViewportOffset } from "../hooks/useViewportOffset";
import { useUpdatePTeamMutation } from "../services/tcApi";
import {
  modalCommonButtonStyle,
  maxPTeamNameLengthInHalf,
  maxContactInfoLengthInHalf,
} from "../utils/const";
import { errorToString, countFullWidthAndHalfWidthCharacters } from "../utils/func";

export function PTeamGeneralSetting(props) {
  const { pteam } = props;
  const { t } = useTranslation("components", { keyPrefix: "PTeamGeneralSetting" });

  const [pteamName, setPTeamName] = useState(pteam.pteam_name);
  const [contactInfo, setContactInfo] = useState(pteam.contact_info);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteConfirmName, setDeleteConfirmName] = useState("");

  const [updatePTeam] = useUpdatePTeamMutation();

  const { enqueueSnackbar } = useSnackbar();
  const viewportOffsetTop = useViewportOffset();

  const operationError = (error) =>
    enqueueSnackbar(t("operationFailed", { error: errorToString(error) }), { variant: "error" });

  const handlePTeamNameSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxPTeamNameLengthInHalf) {
      enqueueSnackbar(
        t("teamNameTooLong", {
          maxHalf: maxPTeamNameLengthInHalf,
          maxFull: Math.floor(maxPTeamNameLengthInHalf / 2),
        }),
        {
          variant: "error",
          style: {
            marginTop: `${viewportOffsetTop}px`,
          },
        },
      );
    } else {
      setPTeamName(string);
    }
  };

  const handleContactInfoSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxContactInfoLengthInHalf) {
      enqueueSnackbar(
        t("contactInfoTooLong", {
          maxHalf: maxContactInfoLengthInHalf,
          maxFull: Math.floor(maxContactInfoLengthInHalf / 2),
        }),
        {
          variant: "error",
          style: {
            marginTop: `${viewportOffsetTop}px`,
          },
        },
      );
    } else {
      setContactInfo(string);
    }
  };

  const handleUpdatePTeam = async () => {
    const data = {
      pteam_name: pteamName,
      contact_info: contactInfo,
    };
    await updatePTeam({ path: { pteam_id: pteam.pteam_id }, body: data })
      .unwrap()
      .then(() => {
        enqueueSnackbar(t("updateSucceeded"), { variant: "success" });
      })
      .catch((error) => operationError(error));
  };

  const handleOpenDeleteDialog = () => {
    setDeleteConfirmName("");
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setDeleteConfirmName("");
  };

  return (
    <Box>
      <Box mb={4}>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          {t("teamName")}
        </Typography>
        <TextField
          size="small"
          value={pteamName}
          onChange={(event) => handlePTeamNameSetting(event.target.value)}
          variant="outlined"
          placeholder={t("teamNamePlaceholder", {
            maxHalf: maxPTeamNameLengthInHalf,
            maxFull: Math.floor(maxPTeamNameLengthInHalf / 2),
          })}
          sx={{ marginRight: "10px", minWidth: "800px" }}
        />
      </Box>
      <Box mb={4}>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          {t("contactInfo")}
        </Typography>
        <TextField
          size="small"
          value={contactInfo}
          onChange={(event) => handleContactInfoSetting(event.target.value)}
          variant="outlined"
          placeholder={t("contactInfoPlaceholder", {
            maxHalf: maxContactInfoLengthInHalf,
            maxFull: Math.floor(maxContactInfoLengthInHalf / 2),
          })}
          sx={{ marginRight: "10px", minWidth: "800px" }}
        />
      </Box>
      <Divider />
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <Button onClick={() => handleUpdatePTeam()} sx={{ ...modalCommonButtonStyle, ml: 1 }}>
          {t("save")}
        </Button>
      </Box>

      <Box
        mt={4}
        p={2}
        sx={{
          border: "1px solid",
          borderColor: "error.main",
          borderRadius: 1,
        }}
      >
        <Box
          display="flex"
          alignItems={{ xs: "flex-start", sm: "center" }}
          justifyContent="space-between"
          flexDirection={{ xs: "column", sm: "row" }}
          gap={2}
        >
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600 }} color="error">
              このチームを削除
            </Typography>
            <Typography variant="body2" color="text.secondary">
              削除すると、全サービス・チケット・データが完全に失われます。
            </Typography>
          </Box>
          <Button
            variant="contained"
            color="error"
            onClick={handleOpenDeleteDialog}
            sx={{ width: { xs: "100%", sm: "auto" } }}
          >
            削除
          </Button>
        </Box>
      </Box>

      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6">チームの削除</Typography>
        </DialogTitle>
        <DialogContent>
          <Typography mb={2}>
            この操作は取り消せません。「{pteam.pteam_name}
            」に関連する全サービス・チケット・データが完全に削除されます。
          </Typography>
          <Typography variant="body2" mb={1}>
            確認のため「{pteam.pteam_name}」と入力してください:
          </Typography>
          <TextField
            size="small"
            fullWidth
            value={deleteConfirmName}
            onChange={(e) => setDeleteConfirmName(e.target.value)}
            placeholder={pteam.pteam_name}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>キャンセル</Button>
          <Button
            disabled={deleteConfirmName !== pteam.pteam_name}
            onClick={handleCloseDeleteDialog}
            color="error"
            variant="contained"
          >
            このチームを削除
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
PTeamGeneralSetting.propTypes = {
  pteam: PropTypes.object.isRequired,
};
