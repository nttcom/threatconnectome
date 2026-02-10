import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  TextField,
  Typography,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

import dialogStyle from "../../cssModule/dialog.module.css";
import { useViewportOffset } from "../../hooks/useViewportOffset";
import { useCreatePTeamMutation } from "../../services/tcApi";
import {
  maxPTeamNameLengthInHalf,
  maxContactInfoLengthInHalf,
  maxSlackWebhookUrlLengthInHalf,
} from "../../utils/const";
import { errorToString, countFullWidthAndHalfWidthCharacters } from "../../utils/func";

export function PTeamCreateModal(props) {
  const { open, onSetOpen, onCloseTeamSelector } = props;
  const { t } = useTranslation("app", { keyPrefix: "PTeamCreateModal" });
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [pteamName, setPTeamName] = useState(null);
  const [contactInfo, setContactInfo] = useState("");
  const [slackUrl, setSlackUrl] = useState("");

  const [createPTeam] = useCreatePTeamMutation();
  const viewportOffsetTop = useViewportOffset();

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

  const handleSlackUrlSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxSlackWebhookUrlLengthInHalf) {
      enqueueSnackbar(
        t("slackUrlTooLong", {
          maxHalf: maxSlackWebhookUrlLengthInHalf,
          maxFull: Math.floor(maxSlackWebhookUrlLengthInHalf / 2),
        }),
        {
          variant: "error",
          style: {
            marginTop: `${viewportOffsetTop}px`,
          },
        },
      );
    } else {
      setSlackUrl(string);
    }
  };

  useEffect(() => {
    onCloseTeamSelector();
    setPTeamName(null);
    setContactInfo("");
    setSlackUrl("");
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [open]);

  const handleCreate = async () => {
    const data = {
      pteam_name: pteamName,
      contact_info: contactInfo,
      alert_slack: { enable: true, webhook_url: slackUrl },
    };
    await createPTeam({ body: data })
      .unwrap()
      .then(async (data) => {
        enqueueSnackbar(t("createSucceeded"), { variant: "success" });
        onSetOpen(false);
        // fix user.pteams before navigating, to avoid overwriting pteamId by pages/App.jsx.
        const newParams = new URLSearchParams();
        newParams.set("pteamId", data.pteam_id);
        navigate("/pteam?" + newParams.toString());
      })
      .catch((error) =>
        enqueueSnackbar(t("operationFailed", { error: errorToString(error) }), {
          variant: "error",
        }),
      );
  };

  return (
    <>
      <Dialog fullWidth open={open} onClose={() => onSetOpen(false)}>
        <DialogTitle>
          <Box display="flex" flexDirection="row">
            <Typography className={dialogStyle.dialog_title}>{t("title")}</Typography>
            <Box flexGrow={1} />
            <IconButton onClick={() => onSetOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column">
            <TextField
              label={t("teamName")}
              onChange={(event) => handlePTeamNameSetting(event.target.value)}
              placeholder={t("teamNamePlaceholder", {
                maxHalf: maxPTeamNameLengthInHalf,
                maxFull: Math.floor(maxPTeamNameLengthInHalf / 2),
              })}
              required
              error={!pteamName}
              margin="dense"
            ></TextField>
            <TextField
              label={t("contactInfo")}
              onChange={(event) => handleContactInfoSetting(event.target.value)}
              placeholder={t("contactInfoPlaceholder", {
                maxHalf: maxContactInfoLengthInHalf,
                maxFull: Math.floor(maxContactInfoLengthInHalf / 2),
              })}
              margin="dense"
            ></TextField>
            <TextField
              label={t("slackWebhook")}
              onChange={(event) => handleSlackUrlSetting(event.target.value)}
              placeholder={t("slackPlaceholder", {
                maxHalf: maxSlackWebhookUrlLengthInHalf,
                maxFull: Math.floor(maxSlackWebhookUrlLengthInHalf / 2),
              })}
              margin="dense"
            ></TextField>
          </Box>
        </DialogContent>
        <DialogActions className={dialogStyle.action_area}>
          <Button onClick={handleCreate} disabled={!pteamName} className={dialogStyle.submit_btn}>
            {t("create")}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

PTeamCreateModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
  onCloseTeamSelector: PropTypes.func.isRequired,
};
