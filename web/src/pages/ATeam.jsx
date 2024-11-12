import { Avatar, Box, MenuItem, Tab, Tabs, TextField, Tooltip } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation } from "react-router";

import { ATeamLabel } from "../components/ATeamLabel";
import { ATeamMember } from "../components/ATeamMember";
import { ATeamWatching } from "../components/ATeamWatching";
import { TabPanel } from "../components/TabPanel";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import {
  useGetATeamAuthQuery,
  useGetATeamMembersQuery,
  useGetUserMeQuery,
} from "../services/tcApi";
import { getATeam } from "../slices/ateam";
import { noATeamMessage, experienceColors } from "../utils/const";
import { a11yProps, errorToString } from "../utils/func.js";

export function ATeam() {
  const [filterMode, setFilterMode] = useState("ATeam");
  const [tabValue, setTabValue] = useState(0);

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const ateamId = params.get("ateamId");
  const ateam = useSelector((state) => state.ateam.ateam);

  const dispatch = useDispatch();

  const filterModes = ["All", "ATeam"];

  const skip = useSkipUntilAuthTokenIsReady() || !ateamId;
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });
  const {
    data: authorities,
    error: authoritiesError,
    isLoading: authoritiesIsLoading,
  } = useGetATeamAuthQuery(ateamId, { skip });
  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetATeamMembersQuery(ateamId, { skip });

  useEffect(() => {
    if (!ateamId) return;
    if (!ateam) dispatch(getATeam(ateamId));
  }, [dispatch, ateamId, ateam]);

  const tabHandleChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (skip) return <></>;
  if (!ateamId) return <>{noATeamMessage}</>;

  if (userMeError) return <>{`Cannot get UserInfo: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;
  if (authoritiesError) return <>{`Cannot get ATeamAuth: ${errorToString(authoritiesError)}`}</>;
  if (authoritiesIsLoading) return <>Now loading ATeamAuth...</>;
  if (membersError) return <>{`Cannot get Members: ${errorToString(membersError)}`}</>;
  if (membersIsLoading) return <>Now loading Members...</>;

  if (!ateam) return <></>;

  const isAdmin = (authorities[userMe.user_id] ?? []).includes("admin");

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
