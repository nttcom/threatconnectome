import { Box } from "@mui/material";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import GTeamLabel from "../components/GTeamLabel";
import GTeamMember from "../components/GTeamMember";
import { getGTeam, getGTeamAuth, getGTeamMembers } from "../slices/gteam";
import { noGTeamMessage } from "../utils/const";

export default function GTeam() {
  const user = useSelector((state) => state.user.user);
  const gteamId = useSelector((state) => state.gteam.gteamId);
  const gteam = useSelector((state) => state.gteam.gteam);
  const members = useSelector((state) => state.gteam.members);
  const authorities = useSelector((state) => state.gteam.authorities);

  const dispatch = useDispatch();

  useEffect(() => {
    if (!gteamId) return;
    if (!gteam) dispatch(getGTeam(gteamId));
    if (!members) dispatch(getGTeamMembers(gteamId));
    if (!authorities) dispatch(getGTeamAuth(gteamId));
  }, [dispatch, gteamId, gteam, members, authorities]);

  const isAdmin = (
    authorities?.find((x) => x.user_id === user.user_id)?.authorities ?? []
  ).includes("admin");

  if (!gteamId) return <>{noGTeamMessage}</>;
  if (!user || !gteam || !members || !authorities) return <></>;

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" flexGrow={1} mb={1}>
        <GTeamLabel gteam={gteam} />
      </Box>
      <Box sx={{ width: "100%" }}>
        <GTeamMember
          gteamId={gteamId}
          members={members}
          achievements={[]}
          authorities={authorities}
          isAdmin={isAdmin}
        />
      </Box>
    </>
  );
}
