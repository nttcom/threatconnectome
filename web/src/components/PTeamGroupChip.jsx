import { Box, Chip } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import { getPTeamGroups } from "../slices/pteam";

export function PTeamGroupChip() {
  const dispatch = useDispatch();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const groups = useSelector((state) => state.pteam.groups);

  useEffect(() => {
    if (!pteamId) return;
    if (!groups) {
      dispatch(getPTeamGroups(pteamId));
    }
  }, [pteamId, groups, dispatch]);

  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const selectedGroup = params.get("group") ?? "";

  const handleSelectGroup = (group) => {
    if (group === selectedGroup) {
      params.delete("group");
    } else {
      params.set("group", group);
      params.set("page", 1); // reset page
    }
    navigate(location.pathname + "?" + params.toString());
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
