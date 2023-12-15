import { Clear as ClearIcon } from "@mui/icons-material";
import { Box, IconButton, InputAdornment, TextField, Tabs, Tab } from "@mui/material";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import { GTeamLabel } from "../components/GTeamLabel";
import { GTeamZoneCard } from "../components/GTeamZoneCard";
import { TabPanel } from "../components/TabPanel";
import { ZoneCreateModal } from "../components/ZoneCreateModal";
import { getGTeam, getGTeamZonesSummary } from "../slices/gteam";
import { noGTeamMessage } from "../utils/const";

function SearchField(props) {
  const { word, onApply } = props;
  const [newWord, setNewWord] = useState(word);

  return (
    <>
      <TextField
        variant="standard"
        label={"Search" + (word === newWord ? "" : " (press ENTER to apply)")}
        size="small"
        value={newWord}
        onChange={(event) => setNewWord(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            onApply(event.target.value);
          }
        }}
        sx={{ textTransform: "none", width: "290px" }}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={() => {
                  setNewWord("");
                  onApply("");
                }}
                size="small"
              >
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
    </>
  );
}

SearchField.propTypes = {
  word: PropTypes.string.isRequired,
  onApply: PropTypes.func.isRequired,
};

function a11yProps(index) {
  return {
    id: `zone-card-${index}`,
    "aria-controls": `zone-cardpanel-${index}`,
  };
}

export function Zone() {
  const [value, setValue] = useState(0);
  const gteamId = useSelector((state) => state.gteam.gteamId);
  const gteam = useSelector((state) => state.gteam.gteam);
  const zonesSummary = useSelector((state) => state.gteam.zonesSummary);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  useEffect(() => {
    if (!gteamId) return;
    if (!gteam) dispatch(getGTeam(gteamId));
    if (!zonesSummary) dispatch(getGTeamZonesSummary(gteamId));
  }, [dispatch, gteamId, gteam, zonesSummary]);

  const params = new URLSearchParams(location.search);
  const searchWord = params.get("word")?.trim().toLowerCase() ?? "";

  const handleSearchWord = (word) => {
    params.set("word", word);
    navigate(location.pathname + "?" + params.toString());
  };

  const filterZones = (zones) => {
    if (!zones) return [];
    return zones.filter(
      (zone) => !searchWord?.length > 0 || zone.zone_name.toLowerCase().includes(searchWord)
    );
  };

  if (!gteamId) return <>{noGTeamMessage}</>;
  if (!gteam) return <></>;

  return (
    <>
      <Box display="flex" flexDirection="row">
        <GTeamLabel gteam={gteam} />
        <Box flexGrow={1} />
      </Box>
      <Box display="flex" sx={{ mr: 2 }}>
        <Box flexGrow={1} />
        <Box sx={{ mb: 2, mr: 2 }}>
          <SearchField word={searchWord} onApply={handleSearchWord} />
        </Box>
        <Box display="flex" justifyContent="flex-end" sx={{ mt: 1, mb: 2 }}>
          <ZoneCreateModal gteamId={gteamId} />
        </Box>
      </Box>
      <Box sx={{ width: "100%" }}>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs value={value} onChange={handleChange} aria-label="zoneItem">
            <Tab label="Zone" {...a11yProps(0)} />
            <Tab label="Archived" {...a11yProps(1)} />
          </Tabs>
        </Box>
        <TabPanel value={value} index={0}>
          <GTeamZoneCard zones={filterZones(zonesSummary?.unarchived_zones)} />
        </TabPanel>
        <TabPanel value={value} index={1}>
          <GTeamZoneCard zones={filterZones(zonesSummary?.archived_zones)} archived={true} />
        </TabPanel>
      </Box>
    </>
  );
}
