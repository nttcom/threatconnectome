import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormLabel,
  TextField,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../hooks/auth";
import { useViewportOffset } from "../hooks/useViewportOffset";
import {
  useUpdatePTeamMutation,
  useDeletePTeamMutation,
  useGetUserMeQuery,
} from "../services/tcApi";
import { APIError } from "../utils/APIError";
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

  const { enqueueSnackbar } = useSnackbar();
  const viewportOffsetTop = useViewportOffset();
  const navigate = useNavigate();

  const [updatePTeam] = useUpdatePTeamMutation();
  const [deletePTeam] = useDeletePTeamMutation();

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  if (skip) return <></>;
  if (userMeError)
    throw new APIError(errorToString(userMeError), {
      api: "getUserMe",
    });

  if (userMeIsLoading) return <>{t("loadingUserInfo")}</>;

  const user = userMe.pteam_roles.find(
    (pteam_role) => pteam_role.pteam.pteam_id === pteam.pteam_id,
  );

  if (!user) {
    throw new APIError("PTeam role not found for current user", {
      api: "getUserMe",
    });
  }

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

  const handleDeletePTeam = async () => {
    try {
      await deletePTeam({ path: { pteam_id: pteam.pteam_id } }).unwrap();
      enqueueSnackbar(t("deleteSucceeded"), { variant: "success" });
      navigate("/");
    } catch (error) {
      operationError(error);
    }
  };

  return (
    <Box>
      <Box mb={2}>
        <FormLabel sx={{ fontWeight: "medium" }}>{t("teamName")}</FormLabel>
        <TextField
          size="small"
          value={pteamName}
          onChange={(event) => handlePTeamNameSetting(event.target.value)}
          variant="outlined"
          helperText={t("teamNamePlaceholder", {
            maxHalf: maxPTeamNameLengthInHalf,
            maxFull: Math.floor(maxPTeamNameLengthInHalf / 2),
          })}
          fullWidth
          disabled={!user.is_admin}
        />
      </Box>
      <Box mb={2}>
        <FormLabel sx={{ fontWeight: "medium" }}>{t("contactInfo")}</FormLabel>
        <TextField
          size="small"
          value={contactInfo}
          onChange={(event) => handleContactInfoSetting(event.target.value)}
          variant="outlined"
          helperText={t("contactInfoPlaceholder", {
            maxHalf: maxContactInfoLengthInHalf,
            maxFull: Math.floor(maxContactInfoLengthInHalf / 2),
          })}
          fullWidth
          disabled={!user.is_admin}
        />
      </Box>
      <Divider />
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <Button
          onClick={() => handleUpdatePTeam()}
          sx={{ ...modalCommonButtonStyle, ml: 1 }}
          disabled={!user.is_admin}
        >
          {t("save")}
        </Button>
      </Box>

      {user.is_admin && (
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
                {t("deleteSectionTitle")}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t("deleteSectionDescription")}
              </Typography>
            </Box>
            <Button
              variant="contained"
              color="error"
              onClick={handleOpenDeleteDialog}
              sx={{ width: { xs: "100%", sm: "auto" } }}
            >
              {t("deleteButton")}
            </Button>
          </Box>
        </Box>
      )}

      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6">{t("deleteDialogTitle")}</Typography>
        </DialogTitle>
        <DialogContent>
          <Typography mb={2} sx={{ whiteSpace: "pre-wrap" }}>
            {t("deleteDialogDescription", { teamName: pteam.pteam_name })}
          </Typography>
          <Typography variant="body2" mb={1} sx={{ whiteSpace: "pre-wrap" }}>
            {t("deleteDialogConfirmLabel", { teamName: pteam.pteam_name })}
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
          <Button onClick={handleCloseDeleteDialog}>{t("deleteDialogCancel")}</Button>
          <Button
            disabled={deleteConfirmName !== pteam.pteam_name}
            onClick={async () => {
              await handleDeletePTeam();
            }}
            color="error"
            variant="contained"
          >
            {t("deleteDialogConfirm")}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
PTeamGeneralSetting.propTypes = {
  pteam: PropTypes.object.isRequired,
};
