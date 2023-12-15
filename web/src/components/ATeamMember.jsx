import { Star as StarIcon, Verified as VerifiedIcon } from "@mui/icons-material";
import {
  Avatar,
  AvatarGroup,
  Badge,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { avatarGroupStyle, difficulty, difficultyColors, experienceColors } from "../utils/const";

import { ATeamInviteModal } from "./ATeamInviteModal";
import { ATeamMemberMenu } from "./ATeamMemberMenu";
import { UUIDTypography } from "./UUIDTypography";

export function ATeamMember(props) {
  const { ateamId, members, achievements, authorities, isAdmin } = props;

  const checkAdmin = (userId) => {
    return (authorities?.find((x) => x.user_id === userId)?.authorities ?? []).includes("admin");
  };

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
                <TableCell sx={{ fontWeight: 900 }}>ACHIEVEMENT</TableCell>
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
                          {achievements &&
                            achievements
                              .filter(
                                (achievement) =>
                                  achievement.email === member.email &&
                                  achievement.badge_id === member.favorite_badge
                              )
                              .map((achievement, index) => (
                                <Tooltip
                                  arrow
                                  describeChild
                                  key={index}
                                  placement="bottom-start"
                                  title={`${achievement.badge_name} *`}
                                  sx={{ m: 0.5 }}
                                >
                                  <Badge
                                    anchorOrigin={{
                                      horizontal: "right",
                                      vertical: "bottom",
                                    }}
                                    badgeContent={<StarIcon color="warning" />}
                                    overlap="circular"
                                  >
                                    <Avatar
                                      alt={achievement.badge_name.slice(0, 1)}
                                      src={achievement.image_url}
                                      variant="square"
                                      sx={{
                                        border: 2,
                                        borderColor: difficultyColors[achievement.difficulty],
                                      }}
                                    >
                                      {/* default badge image */}
                                      {achievement.image_url ? "" : <VerifiedIcon />}
                                    </Avatar>
                                  </Badge>
                                </Tooltip>
                              ))}
                          {achievements?.filter((achievement) => achievement.email === member.email)
                            ?.length > 0 && (
                            <Box alignItems="center" display="flex" flexDirection="row" pl={1}>
                              <AvatarGroup
                                max={3}
                                variant="rounded"
                                sx={{ mx: 0.5, ...avatarGroupStyle }}
                              >
                                {achievements
                                  ?.filter((achievement) => achievement.email === member.email)
                                  .sort(
                                    (a, b) =>
                                      difficulty.indexOf(a.difficulty) -
                                      difficulty.indexOf(b.difficulty)
                                  )
                                  .map((achievement, index) => (
                                    <Tooltip
                                      arrow
                                      key={index}
                                      placement="bottom-start"
                                      title={achievement.badge_name}
                                      sx={{ m: 0.5 }}
                                    >
                                      <Avatar
                                        alt={achievement.badge_name.slice(0, 1)}
                                        className={achievement.difficulty}
                                        src={achievement.image_url}
                                        variant="square"
                                      >
                                        {/* default badge image */}
                                        {achievement.image_url ? "" : <VerifiedIcon />}
                                      </Avatar>
                                    </Tooltip>
                                  ))}
                              </AvatarGroup>
                            </Box>
                          )}
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
  achievements: PropTypes.arrayOf(PropTypes.object).isRequired,
  authorities: PropTypes.arrayOf(PropTypes.object).isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
