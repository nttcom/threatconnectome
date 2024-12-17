import SettingsIcon from "@mui/icons-material/Settings";
import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormLabel,
  IconButton,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import React, { useState } from "react";

import { PTeamServiceImageUploadDeleteButton } from "./PTeamServiceImageUploadDeleteButton";

export function PTeamServiceDetailsSettings() {
  const keywordsList = ["foobar", "keyword"];
  const [currentKeywordsList, setCurrentKeywordsList] = useState(keywordsList);
  const [keywordText, setKeywordText] = useState("");
  const [open, setOpen] = useState(false);
  const [serviceName, setServiceName] = useState("service_name");
  const [keywordAddingMode, setKeywordAddingMode] = useState(false);
  const safetyImpactList = ["negligible", "marginal", "critical", "catastrophic"];
  const [defaultSafetyImpactValue, setDefaultSafetyImpactValue] = useState(safetyImpactList[0]);
  const description =
    "description description description description description description description description description description description description description description description description description description description description description description description description description ";
  const [currentDescription, setCurrentDescription] = useState(description);
  const handleClose = () => {
    setOpen(false);
  };
  const handleClickOpen = () => {
    setOpen(true);
  };
  const handleDelete = (item) => {
    const keywordsListCopy = JSON.parse(JSON.stringify(currentKeywordsList));
    const filteredKeywordsList = keywordsListCopy.filter((keyword) => keyword !== item);
    setCurrentKeywordsList(filteredKeywordsList);
  };
  return (
    <>
      <IconButton onClick={handleClickOpen} sx={{ position: "absolute", right: 0, top: 0 }}>
        <SettingsIcon />
      </IconButton>
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="md">
        <DialogTitle>Service settings</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2}>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <FormLabel required>Name</FormLabel>
              <TextField
                required
                size="small"
                value={serviceName}
                onChange={(e) => setServiceName(e.target.value)}
                helperText={serviceName ? "" : "This field is required."}
                error={!serviceName}
              />
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <FormLabel>Image</FormLabel>
              <Box>
                <Box
                  component="img"
                  sx={{ height: 200, aspectRatio: "4/3" }}
                  src="/images/320x240.png"
                  alt=""
                />
              </Box>
              <Box>
                <PTeamServiceImageUploadDeleteButton />
              </Box>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <FormLabel>Keywords</FormLabel>
              <Box>
                <Stack direction="row" spacing={1} useFlexGap sx={{ flexWrap: "wrap" }}>
                  {currentKeywordsList.map((keyword) => (
                    <Chip key={keyword} label={keyword} onDelete={() => handleDelete(keyword)} />
                  ))}
                </Stack>
                {keywordAddingMode ? (
                  <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
                    <TextField
                      variant="outlined"
                      size="small"
                      value={keywordText}
                      onChange={(e) => setKeywordText(e.target.value)}
                      sx={{ mr: 1 }}
                    />
                    <Button
                      variant="contained"
                      onClick={() => {
                        setKeywordAddingMode(false);
                        setCurrentKeywordsList([...currentKeywordsList, keywordText]);
                        setKeywordText("");
                      }}
                      disabled={!keywordText}
                    >
                      Add
                    </Button>
                    <Button
                      onClick={() => {
                        setKeywordAddingMode(false);
                        setKeywordText("");
                      }}
                    >
                      Cancel
                    </Button>
                  </Box>
                ) : (
                  <Box>
                    <Button onClick={() => setKeywordAddingMode(!keywordAddingMode)}>
                      + Add a new keyword
                    </Button>
                  </Box>
                )}
              </Box>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <FormLabel>Default Safety Impact</FormLabel>
              <ToggleButtonGroup color="primary" value={defaultSafetyImpactValue} exclusive>
                {safetyImpactList.map((value) => (
                  <ToggleButton
                    key={value}
                    value={value}
                    onClick={() => setDefaultSafetyImpactValue(value)}
                  >
                    {value}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>
            <Box>
              <FormLabel>Description</FormLabel>
              <TextField
                multiline
                rows={3}
                fullWidth
                value={currentDescription}
                onChange={(e) => setCurrentDescription(e.target.value)}
              />
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} variant="contained" sx={{ borderRadius: 5, mr: 2, mb: 1 }}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
