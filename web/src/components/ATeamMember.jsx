import { Star as StarIcon } from "@mui/icons-material";
import {
  Avatar,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { experienceColors } from "../utils/const";

import { ATeamInviteModal } from "./ATeamInviteModal";
import { ATeamMemberMenu } from "./ATeamMemberMenu";
import { UUIDTypography } from "./UUIDTypography";

export function ATeamMember(props) {
  const { ateamId, members, authorities, isAdmin } = props;

  const checkAdmin = (userId) => (authorities[userId] ?? []).includes("admin");

  return (
    <>
      <Box sx={{ width: "100%" }}>
        <Box display="flex" justifyContent="flex-end" mb={2}>
          {ateamId && <ATeamInviteModal text="Add member" />}
        </Box>
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="memberTable">
            <TableHead>
              <TableRow>
                <TableCell sx={{ width: "30%", fontWeight: 900 }}>USER(EMAIL)</TableCell>
                <TableCell sx={{ fontWeight: 900 }}>EXPERIENCE in SecOps</TableCell>
                <TableCell sx={{ fontWeight: 900 }} align="right">
                  ACTIONS
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {members &&
                [...Object.values(members)]
                  .sort((a, b) => b.email < a.email)
                  .sort((a, b) => b.years - a.years)
                  .filter((member) => member.disabled === false)
                  .map((member) => (
                    <TableRow
                      key={member.email}
                      sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                    >
                      <TableCell align="left" style={{ width: "30%" }}>
                        <Box display="flex" flexDirection="row">
                          {checkAdmin(member.user_id) && <StarIcon color="warning" />}
                          <Typography>{member.email}</Typography>
                        </Box>
                        <UUIDTypography>{member.user_id}</UUIDTypography>
                      </TableCell>
                      <TableCell align="left">
                        <Box display="flex">
                          <Avatar
                            variant="rounded"
                            sx={{
                              bgcolor: experienceColors[member.years],
                              color: "black",
                              m: 0.5,
                            }}
                          >
                            {member.years}+
                          </Avatar>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <ATeamMemberMenu
                          userId={member.user_id}
                          userEmail={member.email}
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

ATeamMember.propTypes = {
  ateamId: PropTypes.string,
  members: PropTypes.shape({
    user_id: PropTypes.string,
    uid: PropTypes.string,
    email: PropTypes.string,
    disabled: PropTypes.bool,
    years: PropTypes.number,
  }).isRequired,
  authorities: PropTypes.object.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
