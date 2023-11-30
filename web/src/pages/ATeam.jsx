import { Verified as VerifiedIcon } from "@mui/icons-material";
import { Avatar, AvatarGroup, Box, MenuItem, Tab, Tabs, TextField, Tooltip } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import ATeamLabel from "../components/ATeamLabel";
import ATeamMember from "../components/ATeamMember";
import ATeamWatching from "../components/ATeamWatching";
import TabPanel from "../components/TabPanel";
import { getATeam, getATeamAuth, getATeamMembers } from "../slices/ateam";
import { avatarGroupStyle, difficulty, noATeamMessage, experienceColors } from "../utils/const";
import { a11yProps } from "../utils/func.js";

export default function ATeam() {
  const [filterMode, setFilterMode] = useState("ATeam");
  const [tabValue, setTabValue] = useState(0);

  const user = useSelector((state) => state.user.user);
  const ateamId = useSelector((state) => state.ateam.ateamId);
  const ateam = useSelector((state) => state.ateam.ateam);
  const members = useSelector((state) => state.ateam.members);
  const authorities = useSelector((state) => state.ateam.authorities);
  const achievements = []; // TODO: not yet implemented for ateam

  const dispatch = useDispatch();

  const filterModes = ["All", "ATeam"];

  useEffect(() => {
    if (!ateamId) return;
    if (!ateam) dispatch(getATeam(ateamId));
    if (!members) dispatch(getATeamMembers(ateamId));
    if (!authorities) dispatch(getATeamAuth(ateamId));
    // if (!achievements) dispatch(getATeamAchievements(ateamId));
  }, [dispatch, ateamId, ateam, members, authorities /*, achievements*/]);

  const handleFilter = (achievement) => {
    switch (filterMode) {
      case "ATeam":
        return achievement.ateam_id === ateamId;
      case "All":
      default:
        return true;
    }
  };

  const tabHandleChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (!ateamId) return <>{noATeamMessage}</>;
  if (!user || !ateam || !members || !achievements || !authorities) return <></>;

  const isAdmin = (
    authorities?.find((x) => x.user_id === user.user_id)?.authorities ?? []
  ).includes("admin");

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" flexGrow={1} mb={1}>
        <ATeamLabel ateam={ateam} />
        <Box alignItems="flex-end" display="flex" flexDirection="column">
          <TextField
            label="Filter"
            margin="dense"
            onChange={(event) => setFilterMode(event.target.value)}
            select
            size="small"
            value={filterMode}
            sx={{ mx: 1, width: 100 }}
          >
            {filterModes.map((mode) => (
              <MenuItem key={mode} value={mode}>
                {mode}
              </MenuItem>
            ))}
          </TextField>
          <Box alignItems="center" display="flex" flexDirection="row">
            {members &&
              (() => {
                const maxYears = Math.max(...Object.values(members).map((member) => member.years));
                return (
                  <Tooltip
                    arrow
                    placement="bottom-start"
                    title={`${maxYears}+ year${maxYears ? "s" : ""} experience`}
                  >
                    <Avatar
                      variant="rounded"
                      sx={{
                        bgcolor: experienceColors[maxYears],
                        color: "black",
                        m: 0.5,
                      }}
                    >
                      {maxYears}+
                    </Avatar>
                  </Tooltip>
                );
              })()}
            {achievements &&
              (() => {
                const badge_names = achievements.map((achievement) => achievement.badge_name);
                const unique_badge_names = [...new Set(badge_names)].sort();
                const unique_achievements = unique_badge_names.map((name) =>
                  achievements.find((achievement) => achievement.badge_name === name)
                );
                const filtered_achievements = unique_achievements.filter((achievement) =>
                  handleFilter(achievement)
                );
                const sorted_achievements = filtered_achievements.sort(
                  (a, b) => difficulty.indexOf(a.difficulty) - difficulty.indexOf(b.difficulty)
                );
                return (
                  <AvatarGroup max={6} variant="rounded" sx={{ m: 0.5, ...avatarGroupStyle }}>
                    {sorted_achievements.map((achievement) => (
                      <Tooltip
                        arrow
                        describeChild
                        key={achievement.badge_id}
                        placement="bottom-start"
                        title={achievement.badge_name}
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
                );
              })()}
          </Box>
        </Box>
      </Box>
      <Box sx={{ width: "100%" }}>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs value={tabValue} onChange={tabHandleChange} aria-label="ateam tabs">
            <Tab label="Members" {...a11yProps(0)} />
            <Tab label="Watching List" {...a11yProps(1)} />
          </Tabs>
        </Box>
        <TabPanel value={tabValue} index={0}>
          <ATeamMember
            ateamId={ateamId}
            members={members}
            achievements={achievements}
            authorities={authorities}
            isAdmin={isAdmin}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <ATeamWatching ateam={ateam} isAdmin={isAdmin} />
        </TabPanel>
      </Box>
    </>
  );
}
