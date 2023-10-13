import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import PTeamWatcherMenu from "./PTeamWatcherMenu";

export default function PTeamWatcher(props) {
  const { pteam, isAdmin } = props;

  if (!pteam) return <></>;

  const monitorTeams = pteam.ateams;

  return (
    <>
      <Box sx={{ width: "100%" }}>
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="monitorTable">
            <TableHead>
              <TableRow>
                <TableCell sx={{ width: "30%", fontWeight: 900 }}>TEAM NAME</TableCell>
                <TableCell sx={{ fontWeight: 900 }}>CONTACT</TableCell>
                <TableCell sx={{ fontWeight: 900 }} align="right">
                  ACTIONS
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {monitorTeams &&
                monitorTeams.map((monitorTeam, index) => (
                  <TableRow
                    key={monitorTeam.ateam_name}
                    sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                  >
                    <TableCell align="left" style={{ width: "30%" }}>
                      {monitorTeam.ateam_name}
                    </TableCell>
                    <TableCell align="left">{monitorTeam.contact_info}</TableCell>
                    <TableCell align="right">
                      <PTeamWatcherMenu
                        pteam={pteam}
                        watcherAteamId={monitorTeam.ateam_id}
                        watcherAteamName={monitorTeam.ateam_name}
                        isAdmin={isAdmin}
                      />
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </>
  );
}

PTeamWatcher.propTypes = {
  pteam: PropTypes.object.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
