import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  Typography,
} from "@mui/material";
import { red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import { getGTeamZonesSummary } from "../slices/gteam";
import { getAuthorizedZones } from "../slices/user";
import { deleteGTeamZone } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function ZoneDeleteModal(props) {
  const { zone } = props;
  const [openZonedel, setOpenZonedel] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const { enqueueSnackbar } = useSnackbar();

  const handleDelete = async () => {
    await deleteGTeamZone(zone.gteam_id, zone.zone_name)
      .then(async (response) => {
        await Promise.all([
          dispatch(getGTeamZonesSummary(zone.gteam_id)),
          dispatch(getAuthorizedZones()),
          enqueueSnackbar("Delete zone succeeded", { variant: "success" }),
        ]);
        navigate(`..?${params.toString()}`);
      })
      .catch((error) => {
        const resp = error.response ?? { status: "???", statusText: error.toString() };
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" }
        );
      });
  };

  return (
    <>
      <Box mb={1}>
        <Divider sx={{ my: 3 }} />
        <Typography sx={{ fontWeight: 900, color: "error.main" }} mb={1}>
          Delete Zone
        </Typography>
        <Box display="flex" flexDirection="row" alignItems="center" mb={3}>
          <Typography variant="body2" mr={2}>
            Once you delete zone, there is no going back.
          </Typography>
          <Button
            variant="contained"
            color="error"
            sx={{ textTransform: "none" }}
            onClick={() => setOpenZonedel(true)}
          >
            Delete
          </Button>
        </Box>
      </Box>
      <Dialog
        open={openZonedel}
        onClose={() => setOpenZonedel(false)}
        PaperProps={{ sx: { minWidth: "600px", maxWidth: "95%" } }}
      >
        <>
          <DialogTitle>
            <Typography variant="inherit">Confirm</Typography>
          </DialogTitle>
          <DialogContent>
            <Box display="flex" flexDirection="column">
              <Typography align="center">
                Are you sure you want to delete this zone: <b>{zone.zone_name}</b>?
                <br />
                This deletion affects other pteams and topics and actions.
              </Typography>
              <Box display="flex">
                <Box flexGrow={1} />
                <Button
                  onClick={() => setOpenZonedel(false)}
                  sx={{ ...modalCommonButtonStyle, mt: 1 }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleDelete}
                  sx={{ ...modalCommonButtonStyle, ml: 1, mt: 1, color: red[800] }}
                >
                  Delete
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </>
      </Dialog>
    </>
  );
}

ZoneDeleteModal.propTypes = {
  zone: PropTypes.object.isRequired,
};
