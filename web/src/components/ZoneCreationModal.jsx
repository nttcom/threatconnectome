import {
  Button,
  Box,
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
  TextField,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch } from "react-redux";

import { getGTeamZonesSummary } from "../slices/gteam";
import { getAuthorizedZones } from "../slices/user";
import { createGTeamZone } from "../utils/api";
import { commonButtonStyle, modalCommonButtonStyle } from "../utils/const";

export default function ZoneCreationModal(props) {
  const { gteamId } = props;
  const [open, setOpen] = useState(false);
  const [zoneName, setZoneName] = useState(null);
  const [zoneInfo, setZoneInfo] = useState("");

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const operationError = (error) => {
    const resp = error.response ?? { status: "???", statusText: error.toString() };
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  function handleCreate() {
    const data = {
      zone_name: zoneName,
      zone_info: zoneInfo,
    };
    createGTeamZone(gteamId, data)
      .then(async () => {
        await Promise.all([
          setOpen(false),
          dispatch(getGTeamZonesSummary(gteamId)),
          dispatch(getAuthorizedZones()),
          enqueueSnackbar("create zone succeeded", { variant: "success" }),
        ]);
      })
      .catch((error) => operationError(error));
  }

  return (
    <>
      <Button onClick={() => setOpen(true)} sx={{ ...commonButtonStyle }}>
        Create Zone
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        PaperProps={{ sx: { minWidth: "600px", maxWidth: "95%" } }}
      >
        <>
          <DialogTitle>
            <Typography variant="inherit">Create Zone</Typography>
          </DialogTitle>
          <DialogContent>
            <Box display="flex" flexDirection="column">
              <TextField
                label="Zone Name"
                onChange={(event) => setZoneName(event.target.value)}
                required
                error={!zoneName}
                margin="dense"
              ></TextField>
              <TextField
                label="Zone Info"
                onChange={(event) => setZoneInfo(event.target.value)}
                margin="dense"
              ></TextField>

              <Box display="flex">
                <Box flexGrow={1} />
                <Button onClick={() => setOpen(false)} sx={{ ...modalCommonButtonStyle, mt: 1 }}>
                  Cancel
                </Button>
                <Button
                  onClick={handleCreate}
                  disabled={!zoneName}
                  sx={{
                    ...modalCommonButtonStyle,
                    ml: 1,
                    mt: 1,
                  }}
                >
                  Create
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </>
      </Dialog>
    </>
  );
}

ZoneCreationModal.propTypes = {
  gteamId: PropTypes.string.isRequired,
};
