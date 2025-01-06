import { Avatar, Box, MenuItem, Tab, Tabs, TextField, Tooltip } from "@mui/material";
import React, { useState } from "react";
import { useLocation } from "react-router";

import { PTeamLabel } from "../../components/PTeamLabel";
import { TabPanel } from "../../components/TabPanel";
import { useSkipUntilAuthTokenIsReady } from "../../hooks/auth";
import { useGetPTeamMembersQuery } from "../../services/tcApi";
import { experienceColors, noPTeamMessage } from "../../utils/const";
import { a11yProps, errorToString } from "../../utils/func.js";

import { PTeamMember } from "./PTeamMember.jsx";

export function PTeam() {
  const [filterMode, setFilterMode] = useState("PTeam");
  const [tabValue, setTabValue] = useState(0);

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const pteamId = params.get("pteamId");

  const skip = useSkipUntilAuthTokenIsReady() || !pteamId;
  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetPTeamMembersQuery(pteamId, { skip });

  if (!pteamId) return <>{noPTeamMessage}</>;
  if (skip) return <></>;

  if (membersError) return <>{`Cannot get Team: ${errorToString(membersError)}`}</>;
  if (membersIsLoading) return <>Now loading Members...</>;

  const filterModes = ["All", "PTeam"];

  const tabHandleChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" flexGrow={1} mb={1}>
        <PTeamLabel pteamId={pteamId} />
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
          </Tabs>
        </Box>
        <TabPanel value={tabValue} index={0}>
          <PTeamMember pteamId={pteamId} members={members} />
        </TabPanel>
      </Box>
    </>
  );
}
