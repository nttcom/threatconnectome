import { Tabs, Tab } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import { getPTeamGroups } from "../slices/pteam";

export function PTeamGroupChip() {
  const dispatch = useDispatch();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const groups = useSelector((state) => state.pteam.groups);

  const [value, setValue] = React.useState(0);

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

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

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
      <Tabs
        value={value}
        onChange={handleChange}
        variant="scrollable"
        scrollButtons="auto"
        aria-label="scrollable auto tabs example"
      >
        {groups &&
          groups.map((group) => (
            <Tab
              key={group}
              label={group}
              onClick={() => {
                handleSelectGroup(group);
              }}
              sx={{
                textTransform: "none",
                border: `1px solid ${grey[300]}`,
                borderRadius: "0.5rem 0.5rem 0 0",
              }}
            />
          ))}
      </Tabs>
    </>
  );
}
