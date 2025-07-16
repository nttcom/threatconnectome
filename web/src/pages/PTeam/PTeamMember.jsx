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
  useMediaQuery,
} from "@mui/material";
import PropTypes from "prop-types";

import { UUIDTypography } from "../../components/UUIDTypography";
import { experienceColors } from "../../utils/const";

import { PTeamInviteModal } from "./PTeamInviteModal";
import { PTeamMemberMenu } from "./PTeamMemberMenu";

export function PTeamMember(props) {
  const { pteamId, members } = props;
  const isMdDown = useMediaQuery((theme) => theme.breakpoints.down("md"));

  const filteredMembers = members
    ? [...Object.values(members)]
        .sort((memberA, memberB) => memberB.email < memberA.email)
        .sort((memberA, memberB) => memberB.years - memberA.years)
        .filter((member) => member.disabled === false)
    : [];

  return (
    <>
      <Box display="flex" justifyContent="flex-end" mb={2}>
        {pteamId && <PTeamInviteModal pteamId={pteamId} text="Add member" />}
      </Box>
      {isMdDown ? (
        <>
          {filteredMembers.map((member) => (
            <Paper
              key={member.user_id}
              variant="outlined"
              sx={{ boxSizing: "border-box", mb: 2, p: 2, width: "100%" }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  minWidth: 0,
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", minWidth: 0 }}>
                  {member.is_admin && <StarIcon color="warning" />}
                  <Typography
                    variant="subtitle1"
                    sx={{
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                    noWrap
                  >
                    {member.email}
                    fasdfasfasfasdfasdfasfasfdasdfasdfasdfafasdfasdfasdffasdfasdfasdfasdfasfd
                  </Typography>
                </Box>
                <PTeamMemberMenu
                  pteamId={pteamId}
                  memberUserId={member.user_id}
                  userEmail={member.email}
                  isTargetMemberAdmin={member.is_admin}
                />
              </Box>
              <UUIDTypography>{member.user_id}</UUIDTypography>
              <Box display="flex" alignItems="center" mt={1}>
                <Avatar
                  variant="rounded"
                  sx={{
                    bgcolor: experienceColors[member.years],
                    color: "black",
                    mr: 1,
                  }}
                >
                  {member.years}+
                </Avatar>
                <Typography variant="body2">SecOps経験年数</Typography>
              </Box>
            </Paper>
          ))}
        </>
      ) : (
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
              {filteredMembers.map((member) => (
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
      )}
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
