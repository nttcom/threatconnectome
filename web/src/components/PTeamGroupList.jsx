import { Box, Chip } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getPTeamGroups } from "../slices/pteam";

export default function PTeamGroupList() {
  const [selectedGroup, setSelectedGroup] = useState("");

  const dispatch = useDispatch();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const groups = useSelector((state) => state.pteam.groups);

  useEffect(() => {
    if (!pteamId) return;
    if (!groups) {
      dispatch(getPTeamGroups(pteamId));
    }
  }, [pteamId, groups, dispatch]);

  const handleSelectGroup = (group) => {
    if (selectedGroup === group) {
      setSelectedGroup("");
    } else {
      setSelectedGroup(group);
    }
  };

  return (
    <>
      <Box>
        {groups &&
          groups.map((group) => (
            <Chip
              key={group}
              label={group}
              variant={group === selectedGroup ? "" : "outlined"}
              sx={{
                mt: 1,
                borderRadius: "2px",
                border: `1px solid ${grey[300]}`,
                borderLeft: `5px solid ${grey[300]}`,
                mr: 1,
                background: group === selectedGroup ? grey[400] : "",
              }}
              onClick={() => {
                handleSelectGroup(group);
              }}
            />
          ))}
      </Box>
    </>
  );
}
