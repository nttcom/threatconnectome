import {
  Box,
  Button,
  Switch,
  Typography,
  TableContainer,
  Table,
  TableBody,
  TableRow,
  TableCell,
  Paper,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import ZoneDeletion from "../components/ZoneDeletion";
import ZoneMarkItemTab from "../components/ZoneMarkItemTab";
import ZoneSettingsModal from "../components/ZoneSettingsModal";
import { getGTeamZonesSummary } from "../slices/gteam";
import { getAuthorizedZones } from "../slices/user";
import { updateZoneArchived } from "../utils/api";

export default function ZoneEdit() {
  const { zoneName } = useParams();
  const [zoneSettingsModalOpen, setZoneSettingsModalOpen] = useState(false);

  const gteamId = useSelector((state) => state.gteam.gteamId);
  const zonesSummary = useSelector((state) => state.gteam.zonesSummary);

  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();

  useEffect(() => {
    if (!gteamId) return;
    if (!zonesSummary) dispatch(getGTeamZonesSummary(gteamId));
  }, [dispatch, gteamId, zonesSummary]);

  if (!zonesSummary) return <></>;
  const zone =
    [...zonesSummary.archived_zones, ...zonesSummary.unarchived_zones].find(
      (x) => x.zone_name === zoneName
    ) ?? {};

  const handleUpdateArchived = (archived) => {
    const operationDesc = archived ? "Archive zone" : "Unarchive zone";
    const onSuccess = async (success) =>
      await Promise.all([
        dispatch(getGTeamZonesSummary(gteamId)),
        dispatch(getAuthorizedZones()),
        enqueueSnackbar(`${operationDesc} succeeded`, { variant: "success" }),
      ]);
    const onError = (error) =>
      enqueueSnackbar(`${operationDesc} failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });

    const data = { archived: archived };
    updateZoneArchived(gteamId, zoneName, data)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Box display="flex" flexDirection="column" flexGrow={1} my={2}>
        <Box display="flex" alignItems="center">
          <Typography variant="h5" fontWeight={900}>
            {zoneName}
          </Typography>
        </Box>
        <TableContainer component={Paper} sx={{ mt: "20px" }}>
          <Table sx={{ minWidth: 650 }} aria-label="simple table">
            <TableBody>
              <TableRow>
                <TableCell sx={{ width: "13%", bgcolor: grey[100] }}>
                  <Typography variant="subtitle1">Creator</Typography>
                </TableCell>
                <TableCell sx={{ width: "40%", wordBreak: "break-word" }}>
                  {/* TODO: display user name */}
                  {zone?.created_by}
                </TableCell>
                <TableCell />
              </TableRow>
              <TableRow>
                <TableCell sx={{ width: "13%", bgcolor: grey[100] }}>
                  <Typography variant="subtitle1">Info</Typography>
                </TableCell>
                <TableCell sx={{ width: "40%", wordBreak: "break-word" }}>
                  {zone.zone_info ? zone.zone_info : "-"}
                </TableCell>
                <TableCell align="right">
                  <Button
                    onClick={() => setZoneSettingsModalOpen(true)}
                    variant="outlined"
                    size="small"
                    sx={{ textTransform: "none" }}
                  >
                    Edit
                  </Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ width: "13%", bgcolor: grey[100] }}>
                  <Typography variant="subtitle1">Subscribed by</Typography>
                </TableCell>
                <TableCell colSpan={2} sx={{ width: "40%", wordBreak: "break-word" }}>
                  {zone.pteams?.length > 0
                    ? zone.pteams
                        .map((pteam) => pteam.pteam_name)
                        .sort((a, b) => a.localeCompare(b)) // alphabetically
                        .slice(0, 3) // extract top 3
                        .join(",")
                    : "-"}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ width: "13%", bgcolor: grey[100] }}>
                  <Typography variant="subtitle1">Archived</Typography>
                </TableCell>
                <TableCell colSpan={2} sx={{ width: "40%", wordBreak: "break-word" }}>
                  <Switch
                    checked={zone.archived}
                    onChange={() => handleUpdateArchived(!zone.archived)}
                    size="small"
                  />
                  {zone.archived ? "Yes" : "No"}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
      <ZoneSettingsModal
        setShow={setZoneSettingsModalOpen}
        show={zoneSettingsModalOpen}
        gteamId={gteamId}
        zoneName={zoneName}
        currentZoneInfo={zone.zone_info ?? ""}
      />
      <ZoneMarkItemTab zone={zone} />
      <ZoneDeletion zone={zone} />
    </>
  );
}
