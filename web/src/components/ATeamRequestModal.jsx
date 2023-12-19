import ContentCopyIcon from "@mui/icons-material/ContentCopy";
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

import { createATeamWatchingRequest } from "../utils/api";
import { commonButtonStyle, modalCommonButtonStyle } from "../utils/const";

export function ATeamRequestModal(props) {
  const { text } = props;

  const ateamId = useSelector((state) => state.ateam.ateamId);

  const [open, setOpen] = useState(false);
  const [maxUses, setMaxUses] = useState(0);
  const [expiration, setExpiration] = useState(addHours(new Date(), 1)); // Date object
  const [requestLink, setRequestLink] = useState(null);

  const { enqueueSnackbar } = useSnackbar();

  const tokenToLink = (token) =>
    `${window.location.origin}${process.env.PUBLIC_URL}/pteam/watching_request?token=${token}`;

  const handleReset = () => {
    setRequestLink(null);
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
      setRequestLink(tokenToLink(success.data.request_id));
      enqueueSnackbar("Create new watching request succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Create watching request failed: ${error.response?.data?.detail ?? error}`, {
        variant: "error",
      });
    }
    const query = {
      expiration: expiration.toISOString(),
      max_uses: maxUses || null,
    };
    await createATeamWatchingRequest(ateamId, query)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  const now = new Date();

  return (
    <>
      <Button onClick={handleOpen} sx={commonButtonStyle}>
        {text}
      </Button>
      <Dialog open={open} fullWidth>
        <DialogTitle>
          <Typography variant="inherit">Create New Watching Request</Typography>
        </DialogTitle>
        <DialogContent>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            {requestLink ? (
              <Box display="flex" flexDirection="column">
                <Typography>Please share the request link below:</Typography>
                <Box display="flex" justifyContent="center" alignItems="center">
                  <Link href={requestLink} sx={{ overflow: "auto", whiteSpace: "nowrap" }}>
                    {requestLink}
                  </Link>
                  <IconButton onClick={() => navigator.clipboard.writeText(requestLink)}>
                    <ContentCopyIcon />
                  </IconButton>
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
                    <Typography>Max groups: {maxUses || "unlimited"}</Typography>
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
            {requestLink ? "Close" : "Cancel"}
          </Button>
          {!requestLink && (
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

ATeamRequestModal.propTypes = {
  text: PropTypes.oneOfType([PropTypes.string, PropTypes.element]).isRequired,
};
