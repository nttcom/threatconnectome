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
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import {
  maxServiceNameLengthInHalf,
  maxDescriptionLengthInHalf,
  maxKeywordLengthInHalf,
  maxKeywords,
} from "../../../utils/const";
import { errorToString, countFullWidthAndHalfWidthCharacters } from "../../../utils/func";

import { PTeamServiceImageUploadDeleteButton } from "./PTeamServiceImageUploadDeleteButton";

export function PTeamServiceDetailsSettingsView(props) {
  const {
    service,
    updatePTeamServiceFunc,
    updatePTeamServiceThumbnailFunc,
    deletePTeamServiceThumbnailFunc,
    image,
  } = props;

  const [serviceName, setServiceName] = useState(service.service_name);
  const [imageFileData, setImageFileData] = useState(null);
  const [imageDeleteFalg, setImageDeleteFlag] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [currentKeywordsList, setCurrentKeywordsList] = useState(service.keywords);
  const [keywordText, setKeywordText] = useState("");
  const [open, setOpen] = useState(false);
  const [keywordAddingMode, setKeywordAddingMode] = useState(false);
  const [currentDescription, setCurrentDescription] = useState(service.description);
  const safetyImpactList = ["negligible", "marginal", "critical", "catastrophic"];
  const [defaultSafetyImpactValue, setDefaultSafetyImpactValue] = useState(
    service.service_safety_impact,
  );

  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    // Reset the state when switching services
    setServiceName(service.service_name);
    setImageFileData(null);
    setImageDeleteFlag(false);
    setImagePreview(null);
    setCurrentKeywordsList(service.keywords);
    setCurrentDescription(service.description);
    setDefaultSafetyImpactValue(service.service_safety_impact);
  }, [service]);

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
  const handleUpdatePTeamService = async () => {
    const promiseList = [];
    if (imageFileData !== null) {
      promiseList.push(() => updatePTeamServiceThumbnailFunc(imageFileData));
    }

    if (imageDeleteFalg) {
      promiseList.push(() => deletePTeamServiceThumbnailFunc());
    }

    const requestData = {
      service_name: serviceName,
      keywords: currentKeywordsList,
      description: currentDescription,
      service_safety_impact: defaultSafetyImpactValue,
    };
    promiseList.push(() => updatePTeamServiceFunc(requestData));

    Promise.all(promiseList.map((apiFunc) => apiFunc()))
      .then(() => {
        enqueueSnackbar("Update succeeded", { variant: "success" });
      })
      .catch((error) => {
        enqueueSnackbar(`Update failed: ${errorToString(error)}`, { variant: "error" });
      });
  };

  const handleServiceNameLengthCheck = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxServiceNameLengthInHalf) {
      enqueueSnackbar(
        `Too long service name. Max length is ${maxServiceNameLengthInHalf} in half-width or ${Math.floor(maxServiceNameLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
        },
      );
    } else {
      setServiceName(string);
    }
  };

  const handleKeywordLengthCheck = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxKeywordLengthInHalf) {
      enqueueSnackbar(
        `Too long description. Max length is ${maxKeywordLengthInHalf} in half-width or ${Math.floor(maxKeywordLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
        },
      );
    } else {
      setKeywordText(string);
    }
  };

  const handleDescriptionLengthCheck = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxDescriptionLengthInHalf) {
      enqueueSnackbar(
        `Too long keyword. Max length is ${maxDescriptionLengthInHalf} in half-width or ${Math.floor(maxDescriptionLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
        },
      );
    } else {
      setCurrentDescription(string);
    }
  };

  const handleKeywordCountCheck = () => {
    if (currentKeywordsList.length >= maxKeywords) {
      setKeywordAddingMode(false);
      enqueueSnackbar(`Too many keywords, max number: ${maxKeywords}`, { variant: "error" });
    } else {
      setKeywordAddingMode(!keywordAddingMode);
    }
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
                onChange={(e) => handleServiceNameLengthCheck(e.target.value)}
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
                  src={imagePreview ? imagePreview : image}
                  alt=""
                />
              </Box>
              <Box>
                <PTeamServiceImageUploadDeleteButton
                  setImageFileData={setImageFileData}
                  setImageDeleteFlag={setImageDeleteFlag}
                  setImagePreview={setImagePreview}
                />
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
                  <Box sx={{ mt: 1 }}>
                    <TextField
                      variant="outlined"
                      size="small"
                      value={keywordText}
                      onChange={(e) => handleKeywordLengthCheck(e.target.value)}
                      sx={{ mr: 1 }}
                      error={currentKeywordsList.includes(keywordText)}
                      helperText={
                        currentKeywordsList.includes(keywordText)
                          ? "Same keyword already exists."
                          : ""
                      }
                    />
                    <Button
                      variant="contained"
                      onClick={() => {
                        setKeywordAddingMode(false);
                        setCurrentKeywordsList([...currentKeywordsList, keywordText]);
                        setKeywordText("");
                      }}
                      disabled={!keywordText || currentKeywordsList.includes(keywordText)}
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
                    <Button onClick={handleKeywordCountCheck}>+ Add a new keyword</Button>
                  </Box>
                )}
              </Box>
            </Box>
            <Box>
              <FormLabel>Description</FormLabel>
              <TextField
                multiline
                rows={3}
                fullWidth
                value={currentDescription}
                onChange={(e) => handleDescriptionLengthCheck(e.target.value)}
              />
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
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              handleClose();
              handleUpdatePTeamService();
            }}
            variant="contained"
            sx={{ borderRadius: 5, mr: 2, mb: 1 }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

PTeamServiceDetailsSettingsView.propTypes = {
  service: PropTypes.object.isRequired,
  updatePTeamServiceFunc: PropTypes.func.isRequired,
  updatePTeamServiceThumbnailFunc: PropTypes.func.isRequired,
  deletePTeamServiceThumbnailFunc: PropTypes.func.isRequired,
  image: PropTypes.string.isRequired,
};
