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

import ATeamRequestModal from "./ATeamRequestModal";
import ATeamWatchingMenu from "./ATeamWatchingMenu";

export default function ATeamWatching(props) {
  const { ateam, isAdmin } = props;

  if (!ateam) return <></>;

  const monitorTeams = ateam.pteams;

  return (
    <>
      <Box sx={{ width: "100%" }}>
        <Box display="flex" justifyContent="flex-end" mb={2}>
          <ATeamRequestModal text="New Watching Request" />
        </Box>
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
                    key={monitorTeam.pteam_name}
                    sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                  >
                    <TableCell align="left" style={{ width: "30%" }}>
                      {monitorTeam.pteam_name}
                    </TableCell>
                    <TableCell align="left">{monitorTeam.contact_info}</TableCell>
                    <TableCell align="right">
                      <ATeamWatchingMenu
                        ateam={ateam}
                        watchingPteamId={monitorTeam.pteam_id}
                        watchingPteamName={monitorTeam.pteam_name}
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

ATeamWatching.propTypes = {
  ateam: PropTypes.object.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
