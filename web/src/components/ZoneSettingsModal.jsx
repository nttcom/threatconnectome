import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";

import { getGTeamZonesSummary } from "../slices/gteam";
import { getAuthorizedZones } from "../slices/user";
import { updateZone } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function ZoneSettingsModal(props) {
  const { setShow, show, gteamId, zoneName, currentZoneInfo } = props;

  const [zoneInfo, setZoneInfo] = useState(currentZoneInfo);
  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();

  useEffect(() => {
    setZoneInfo(currentZoneInfo);
  }, [show, currentZoneInfo]);

  const handleClose = () => setShow(false);

  const operationError = (error) => {
    const resp = error.response;
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  const handleUpdateZone = async () => {
    const data = { zone_info: zoneInfo };
    await updateZone(gteamId, zoneName, data)
      .then(async () => {
        await Promise.all([
          dispatch(getGTeamZonesSummary(gteamId)),
          dispatch(getAuthorizedZones()),
          enqueueSnackbar("update zone info succeeded", { variant: "success" }),
          handleClose(),
        ]);
      })
      .catch((error) => operationError(error));
  };

  return (
    <Dialog
      onClose={handleClose}
      open={show}
      PaperProps={{ sx: { minWidth: "600px", maxWidth: "95%" } }}
    >
      <DialogTitle>
        <Typography variant="inherit">Edit Zone Info</Typography>
      </DialogTitle>
      <DialogContent>
        <Box display="flex" flexDirection="column">
          <TextField
            disabled
            id="outlined-disabled"
            label="Zone Name"
            defaultValue={zoneName}
            sx={{ m: 1 }}
          />
          <TextField
            label="Zone Info"
            margin="dense"
            value={zoneInfo}
            onChange={(event) => setZoneInfo(event.target.value)}
            sx={{ m: 1 }}
            multiline
            maxRows={4}
          />
          <Box display="flex">
            <Box flexGrow={1} />
            <Button onClick={() => setShow(false)} sx={{ ...modalCommonButtonStyle, mt: 1 }}>
              Cancel
            </Button>
            <Button
              onClick={() => handleUpdateZone()}
              sx={{
                ...modalCommonButtonStyle,
                ml: 1,
                mt: 1,
              }}
            >
              Submit
            </Button>
          </Box>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
ZoneSettingsModal.propTypes = {
  setShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  gteamId: PropTypes.string.isRequired,
  zoneName: PropTypes.string.isRequired,
  currentZoneInfo: PropTypes.string.isRequired,
};
