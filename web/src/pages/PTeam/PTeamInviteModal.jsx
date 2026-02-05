import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  Link,
  Slider,
  Typography,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { addHours, isBefore } from "date-fns";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import styles from "../../cssModule/button.module.css";
import dialogStyle from "../../cssModule/dialog.module.css";
import { useCreatePTeamInvitationMutation } from "../../services/tcApi";
import { errorToString } from "../../utils/func";

import { CopiedIcon } from "./CopiedIcon";

export function PTeamInviteModal(props) {
  const { pteamId, text } = props;
  const { t } = useTranslation("pteam", { keyPrefix: "PTeamInviteModal" });

  const [open, setOpen] = useState(false);
  const [maxUses, setMaxUses] = useState(0);
  const [expiration, setExpiration] = useState(addHours(new Date(), 1)); // Date object
  const [invitationLink, setInvitationLink] = useState(null);

  const { enqueueSnackbar } = useSnackbar();

  const [createPTeamInvitation] = useCreatePTeamInvitationMutation();

  const tokenToLink = (token) =>
    `${window.location.origin}${import.meta.env.VITE_PUBLIC_URL}/pteam/join?token=${token}`;
  const handleReset = () => {
    setInvitationLink(null);
    setMaxUses(0);
    setExpiration(addHours(new Date(), 1));
  };
  const handleOpen = () => {
    handleReset();
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };
  const handleCreate = async () => {
    function onSuccess(data) {
      setInvitationLink(tokenToLink(data.invitation_id));
      enqueueSnackbar("Create new invitation succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(t("createInvitationFailed", { error: errorToString(error) }), {
        variant: "error",
      });
    }
    const data = {
      expiration: expiration.toISOString(),
      max_uses: maxUses || null,
    };
    await createPTeamInvitation({ path: { pteam_id: pteamId }, body: data })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  const now = new Date();

  return (
    <>
      <Button className={styles.prominent_btn} onClick={handleOpen}>
        {text}
      </Button>
      <Dialog open={open} onClose={handleClose} fullWidth>
        <DialogTitle>
          <Box display="flex" flexDirection="row">
            <Typography className={dialogStyle.dialog_title}>
              {t("createNewInvitationLink")}
            </Typography>
            <Box flexGrow={1} />
            <IconButton onClick={handleClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            {invitationLink ? (
              <Box display="flex" flexDirection="column">
                <Typography>{t("pleaseShareLink")}</Typography>
                <Box display="flex" justifyContent="center" alignItems="center">
                  <Link href={invitationLink} sx={{ overflow: "auto" }}>
                    {invitationLink}
                  </Link>
                  <CopiedIcon invitationLink={invitationLink} />
                </Box>
              </Box>
            ) : (
              <Grid container alignItems="center">
                <Grid size={{ xs: 12, md: 6 }}>
                  <Box sx={{ p: 1 }}>
                    <DateTimePicker
                      format="yyyy/MM/dd HH:mm"
                      label={t("expirationDate")}
                      mask="____/__/__ __:__"
                      minDateTime={now}
                      value={expiration}
                      onChange={(newDate) => setExpiration(newDate)}
                      slotProps={{
                        textField: {
                          fullWidth: true,
                          margin: "dense",
                          required: true,
                        },
                      }}
                    />
                  </Box>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Box display="flex" flexDirection="column" justifyContent="center" sx={{ p: 1 }}>
                    <Typography>{t("maxUses", { count: maxUses || t("unlimited") })}</Typography>
                    <Box mx={1}>
                      <Slider
                        step={1}
                        marks={[0, 1, 5, 10, 15, 20].map((item) => ({
                          label: item || "\u221e", // infinity
                          value: item,
                        }))}
                        max={20}
                        min={0}
                        value={maxUses}
                        onChange={(_, value) => setMaxUses(value)}
                        sx={{ width: "100%" }}
                      />
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            )}
          </LocalizationProvider>
        </DialogContent>
        <DialogActions className={dialogStyle.action_area}>
          {!invitationLink && (
            <Button
              onClick={handleCreate}
              disabled={!isBefore(now, expiration)}
              className={dialogStyle.submit_btn}
            >
              {t("create")}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
}

PTeamInviteModal.propTypes = {
  pteamId: PropTypes.string.isRequired,
  text: PropTypes.oneOfType([PropTypes.string, PropTypes.element]).isRequired,
};
