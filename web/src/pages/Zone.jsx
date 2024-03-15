import { Clear as ClearIcon } from "@mui/icons-material";
import { Box, IconButton, InputAdornment, TextField, Tabs, Tab } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router";

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

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const searchWord = params.get("word")?.trim().toLowerCase() ?? "";

  const handleSearchWord = (word) => {
    params.set("word", word);
    navigate(location.pathname + "?" + params.toString());
  };

  return (
    <>
      <Box display="flex" flexDirection="row">
        <Box flexGrow={1} />
      </Box>
      <Box display="flex" sx={{ mb: -5, mr: 1 }}>
        <Box flexGrow={1} />
        <Box sx={{ mb: 2, mr: 2 }}>
          <SearchField word={searchWord} onApply={handleSearchWord} />
        </Box>
      </Box>
      <Box sx={{ width: "100%" }}>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs value={value} onChange={handleChange} aria-label="zoneItem">
            <Tab label="Zone" {...a11yProps(0)} />
            <Tab label="Archived" {...a11yProps(1)} />
          </Tabs>
        </Box>
      </Box>
    </>
  );
}
