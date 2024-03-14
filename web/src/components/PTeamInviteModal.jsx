import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Link,
  Slider,
  TextField,
  Typography,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { addHours, isBefore } from "date-fns";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useSelector } from "react-redux";

import styles from "../cssModule/button.module.css";
import { createPTeamInvitation } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

import { CopiedIcon } from "./CopiedIcon";

export function PTeamInviteModal(props) {
  const { text } = props;

  const pteamId = useSelector((state) => state.pteam.pteamId);

  const [open, setOpen] = useState(false);
  const [maxUses, setMaxUses] = useState(0);
  const [expiration, setExpiration] = useState(addHours(new Date(), 1)); // Date object
  const [invitationLink, setInvitationLink] = useState(null);

  const { enqueueSnackbar } = useSnackbar();

  const tokenToLink = (token) =>
    `${window.location.origin}${process.env.PUBLIC_URL}/pteam/join?token=${token}`;
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
    function onSuccess(success) {
      setInvitationLink(tokenToLink(success.data.invitation_id));
      enqueueSnackbar("Create new invitation succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Create invitation failed: ${error.response?.data?.detail ?? error}`, {
        variant: "error",
      });
    }
    const query = {
      expiration: expiration.toISOString(),
      max_uses: maxUses || null,
    };
    await createPTeamInvitation(pteamId, query)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  const now = new Date();

  return (
    <>
      <Button className={styles.prominent_btn} onClick={handleOpen}>
        {text}
      </Button>
      <Dialog open={open} fullWidth>
        <DialogTitle>
          <Typography variant="inherit">Create New Invitation Link</Typography>
        </DialogTitle>
        <DialogContent>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            {invitationLink ? (
              <Box display="flex" flexDirection="column">
                <Typography>Please share the invitation link below:</Typography>
                <Box display="flex" justifyContent="center" alignItems="center">
                  <Link href={invitationLink} sx={{ overflow: "auto" }}>
                    {invitationLink}
                  </Link>
                  <CopiedIcon invitationLink={invitationLink} />
                </Box>
              </Box>
            ) : (
              <Grid container alignItems="center">
                <Grid item p={1} xs={6} sm={6}>
                  <DateTimePicker
                    inputFormat="yyyy/MM/dd HH:mm"
                    label="Expiration Date (future date)"
                    mask="____/__/__ __:__"
                    minDateTime={now}
                    value={expiration}
                    onChange={(newDate) => setExpiration(newDate)}
                    renderInput={(params) => (
                      <TextField fullWidth margin="dense" required {...params} />
                    )}
                  />
                </Grid>
                <Grid item p={1} xs={6} sm={6}>
                  <Box display="flex" flexDirection="column" justifyContent="center">
                    <Typography>Max uses: {maxUses || "unlimited"}</Typography>
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
        <DialogActions>
          <Button onClick={handleClose} sx={modalCommonButtonStyle}>
            {invitationLink ? "Close" : "Cancel"}
          </Button>
          {!invitationLink && (
            <Button
              onClick={handleCreate}
              disabled={!isBefore(now, expiration)}
              sx={modalCommonButtonStyle}
            >
              Create
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
}

PTeamInviteModal.propTypes = {
  text: PropTypes.oneOfType([PropTypes.string, PropTypes.element]).isRequired,
};
