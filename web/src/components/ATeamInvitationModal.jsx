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
import { AdapterMoment } from "@mui/x-date-pickers/AdapterMoment";
import moment from "moment";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useSelector } from "react-redux";

import { createATeamInvitation } from "../utils/api";
import { commonButtonStyle, modalCommonButtonStyle } from "../utils/const";

export default function ATeamInvitationModal(props) {
  const { text } = props;

  const ateamId = useSelector((state) => state.ateam.ateamId);

  const [open, setOpen] = useState(false);
  const [data, setData] = useState({});
  const [invitationLink, setInvitationLink] = useState(null);

  const { enqueueSnackbar } = useSnackbar();

  const tokenToLink = (token) =>
    `${window.location.origin}${process.env.PUBLIC_URL}/ateam/join?token=${token}`;
  const handleReset = () => {
    setInvitationLink(null);
    setData({
      expiration: moment().add(1, "hours").toDate(),
      max_uses: 0,
    });
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
      expiration: data.expiration.toISOString(),
      max_uses: data.max_uses || null,
    };
    await createATeamInvitation(ateamId, query)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  const now = moment();

  if (!ateamId) return <></>;

  return (
    <>
      <Button onClick={handleOpen} sx={commonButtonStyle}>
        {text}
      </Button>
      <Dialog open={open} fullWidth>
        <DialogTitle>
          <Typography variant="inherit">Create New Invitation Link</Typography>
        </DialogTitle>
        <DialogContent>
          <LocalizationProvider dateAdapter={AdapterMoment}>
            {invitationLink ? (
              <Box display="flex" flexDirection="column">
                <Typography>Please share the invitation link below:</Typography>
                <Box display="flex" justifyContent="center" alignItems="center">
                  <Link href={invitationLink} sx={{ overflow: "auto", whiteSpace: "nowrap" }}>
                    {invitationLink}
                  </Link>
                  <IconButton onClick={() => navigator.clipboard.writeText(invitationLink)}>
                    <ContentCopyIcon />
                  </IconButton>
                </Box>
              </Box>
            ) : (
              <Grid container alignItems="center">
                <Grid item p={1} xs={6} sm={6}>
                  <DateTimePicker
                    inputFormat="YYYY/MM/DD HH:mm"
                    label="Expiration Date (future date)"
                    mask="____/__/__ __:__"
                    minDateTime={now}
                    onChange={(moment) =>
                      setData({ ...data, expiration: moment ? moment.toDate() : "" })
                    }
                    renderInput={(params) => (
                      <TextField
                        fullWidth
                        margin="dense"
                        required
                        {...params}
                        sx={{ width: "100%" }}
                      />
                    )}
                    value={data.expiration}
                  />
                </Grid>
                <Grid item p={1} xs={6} sm={6}>
                  <Box display="flex" flexDirection="column" justifyContent="center">
                    <Typography>Max uses: {data.max_uses || "unlimited"}</Typography>
                    <Box mx={1}>
                      <Slider
                        step={1}
                        marks={[0, 1, 5, 10, 15, 20].map((item) => ({
                          label: item || "\u221e", // infinity
                          value: item,
                        }))}
                        max={20}
                        min={0}
                        onChange={(_, value) => setData({ ...data, max_uses: value })}
                        value={data.max_uses}
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
              disabled={!now.isBefore(data.expiration)}
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

ATeamInvitationModal.propTypes = {
  text: PropTypes.oneOfType([PropTypes.string, PropTypes.element]).isRequired,
};
