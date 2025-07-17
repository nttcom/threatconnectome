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

import { UUIDTypography } from "../../components/UUIDTypography";
import { experienceColors } from "../../utils/const";
import { checkAdmin } from "../../utils/func.js";

import { PTeamInviteModal } from "./PTeamInviteModal";
import { PTeamMemberMenu } from "./PTeamMemberMenu";

export function PTeamMember(props) {
  const { pteamId, members } = props;

  return (
    <>
      <Box sx={{ width: "100%" }}>
        <Box display="flex" justifyContent="flex-end" mb={2}>
          {pteamId && <PTeamInviteModal pteamId={pteamId} text="Add member" />}
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
                  .sort((memberA, memberB) => memberB.email < memberA.email)
                  .sort((memberA, memberB) => memberB.years - memberA.years)
                  .filter((member) => member.disabled === false)
                  .map((member) => (
                    <TableRow
                      key={member.user_id}
                      sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                    >
                      <TableCell align="left" style={{ width: "30%" }}>
                        <Box display="flex" flexDirection="row">
                          {member.is_admin && <StarIcon color="warning" />}
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
                        <PTeamMemberMenu
                          pteamId={pteamId}
                          memberUserId={member.user_id}
                          userEmail={member.email}
                          isTargetMemberAdmin={member.is_admin}
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

PTeamMember.propTypes = {
  pteamId: PropTypes.string,
  members: PropTypes.objectOf(
    PropTypes.shape({
      user_id: PropTypes.string.isRequired,
      uid: PropTypes.string,
      email: PropTypes.string.isRequired,
      disabled: PropTypes.bool,
      years: PropTypes.number.isRequired,
    }),
  ).isRequired,
};
