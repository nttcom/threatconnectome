import { Avatar, Box, MenuItem, Tab, Tabs, TextField, Tooltip } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { PTeamLabel } from "../components/PTeamLabel";
import { PTeamMember } from "../components/PTeamMember";
import { PTeamWatcher } from "../components/PTeamWatcher";
import { TabPanel } from "../components/TabPanel";
import { getPTeam, getPTeamAuth, getPTeamMembers } from "../slices/pteam";
import { experienceColors, noPTeamMessage } from "../utils/const";
import { a11yProps } from "../utils/func.js";

export function PTeam() {
  const [filterMode, setFilterMode] = useState("PTeam");
  const [tabValue, setTabValue] = useState(0);

  const user = useSelector((state) => state.user.user);
  const pteam = useSelector((state) => state.pteam.pteam);
  const pteamId = useSelector((state) => state.pteam.pteamId);
  const members = useSelector((state) => state.pteam.members);
  const authorities = useSelector((state) => state.pteam.authorities);
  const dispatch = useDispatch();

  useEffect(() => {
    if (!pteamId) return;
    if (!pteam) dispatch(getPTeam(pteamId));
    if (!members) dispatch(getPTeamMembers(pteamId));
    if (!authorities) dispatch(getPTeamAuth(pteamId));
  }, [dispatch, pteamId, pteam, members, authorities]);

  const checkAdmin = (userId) => {
    return (authorities?.find((x) => x.user_id === userId)?.authorities ?? []).includes("admin");
  };

  const filterModes = ["All", "PTeam"];

  const tabHandleChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (!pteamId) return <>{noPTeamMessage}</>;
  if (!user || !pteam || !members || !authorities) return <></>;
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
