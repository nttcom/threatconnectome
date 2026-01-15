import { Avatar, Box, Tab, Tabs, Tooltip } from "@mui/material";
import { useState } from "react";
import { useLocation } from "react-router-dom";

import { PTeamLabel } from "../../components/PTeamLabel";
import { TabPanel } from "../../components/TabPanel";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetPTeamMembersQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { experienceColors, noPTeamMessage } from "../../utils/const";
import { a11yProps, errorToString } from "../../utils/func";

import { PTeamMember } from "./PTeamMember.jsx";

export function PTeam() {
  const [tabValue, setTabValue] = useState(0);

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const pteamId = params.get("pteamId");

  const skip = useSkipUntilAuthUserIsReady() || !pteamId;
  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetPTeamMembersQuery({ path: { pteam_id: pteamId } }, { skip });

  if (!pteamId) return <>{noPTeamMessage}</>;
  if (skip) return <></>;

  if (membersError)
    throw new APIError(errorToString(membersError), {
      api: "getPTeamMembers",
    });

  if (membersIsLoading) return <>Now loading Members...</>;

  const tabHandleChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" flexGrow={1} mb={1}>
        <PTeamLabel pteamId={pteamId} />
        <Box alignItems="flex-end" display="flex" flexDirection="column">
          <Box alignItems="center" display="flex" flexDirection="row">
            {members &&
              (() => {
                const maxYears = Math.max(members.map((member) => member.years));
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
