import { Verified as VerifiedIcon } from "@mui/icons-material";
import { Avatar, AvatarGroup, Box, MenuItem, Tab, Tabs, TextField, Tooltip } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import PTeamLabel from "../components/PTeamLabel";
import PTeamMember from "../components/PTeamMember";
import PTeamWatcher from "../components/PTeamWatcher";
import TabPanel from "../components/TabPanel";
import { getPTeam, getPTeamAuth, getPTeamMembers, getPTeamAchievements } from "../slices/pteam";
import { avatarGroupStyle, experienceColors, difficulty, noPTeamMessage } from "../utils/const";
import { a11yProps } from "../utils/func.js";

export default function PTeam() {
  const [filterMode, setFilterMode] = useState("pteam");
  const [tabValue, setTabValue] = useState(0);

  const user = useSelector((state) => state.user.user);
  const pteam = useSelector((state) => state.pteam.pteam);
  const pteamId = useSelector((state) => state.pteam.pteamId);
  const members = useSelector((state) => state.pteam.members);
  const achievements = useSelector((state) => state.pteam.achievements);
  const authorities = useSelector((state) => state.pteam.authorities);
  const dispatch = useDispatch();

  useEffect(() => {
    if (!pteamId) return;
    if (!pteam) dispatch(getPTeam(pteamId));
    if (!members) dispatch(getPTeamMembers(pteamId));
    if (!achievements) dispatch(getPTeamAchievements(pteamId));
    if (!authorities) dispatch(getPTeamAuth(pteamId));
  }, [dispatch, pteamId, pteam, members, achievements, authorities]);

  const checkAdmin = (userId) => {
    return (authorities?.find((x) => x.user_id === userId)?.authorities ?? []).includes("admin");
  };

  const filterModes = ["all", "pteam"];

  const handleFilter = (achievement) => {
    switch (filterMode) {
      case "pteam":
        return achievement.pteam_id === pteamId;
      case "all":
      default:
        return true;
    }
  };

  const tabHandleChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (!pteamId) return <>{noPTeamMessage}</>;
  if (!user || !pteam || !members || !achievements || !authorities) return <></>;
  const isAdmin = checkAdmin(user.user_id);

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" flexGrow={1} mb={1}>
        <PTeamLabel />
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
          <Tabs value={tabValue} onChange={tabHandleChange} aria-label="pteam tabs">
            <Tab label="Members" {...a11yProps(0)} />
            <Tab label="Watchers" {...a11yProps(1)} />
          </Tabs>
        </Box>
        <TabPanel value={tabValue} index={0}>
          <PTeamMember
            pteamId={pteamId}
            members={members}
            achievements={achievements}
            authorities={authorities}
            isAdmin={isAdmin}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <PTeamWatcher pteam={pteam} isAdmin={isAdmin} />
        </TabPanel>
      </Box>
    </>
  );
}
