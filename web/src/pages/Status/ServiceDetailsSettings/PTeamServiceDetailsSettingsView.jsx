import { Close as CloseIcon, Settings as SettingsIcon } from "@mui/icons-material";
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
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";

import dialogStyle from "../../../cssModule/dialog.module.css";
import {
  maxServiceNameLengthInHalf,
  maxDescriptionLengthInHalf,
  maxKeywordLengthInHalf,
  maxKeywords,
} from "../../../utils/const";
import { countFullWidthAndHalfWidthCharacters } from "../../../utils/func";

import { PTeamServiceImageUploadDeleteButton } from "./PTeamServiceImageUploadDeleteButton";

export function PTeamServiceDetailsSettingsView(props) {
  const { service, image, onSave } = props;

  const [serviceName, setServiceName] = useState(service.service_name);
  const [imageFileData, setImageFileData] = useState(null);
  const [imageDeleteFlag, setImageDeleteFlag] = useState(false);
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

  const [isChanged, setIsChanged] = useState(false);
  const [isImageChanged, setIsImageChanged] = useState(false);

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
    setIsChanged(false);
  }, [service]);

  useEffect(() => {
    setIsChanged(
      serviceName !== service.service_name ||
        currentKeywordsList.length !== service.keywords.length ||
        currentKeywordsList.some((keyword, index) => keyword !== service.keywords[index]) ||
        currentDescription !== service.description ||
        defaultSafetyImpactValue !== service.service_safety_impact ||
        isImageChanged,
    );
  }, [
    serviceName,
    imageFileData,
    currentKeywordsList,
    currentDescription,
    defaultSafetyImpactValue,
    service,
    isImageChanged,
  ]);

  const handleClose = () => {
    setServiceName(service.service_name);
    setImageFileData(null);
    setImageDeleteFlag(false);
    setImagePreview(null);
    setCurrentKeywordsList(service.keywords);
    setKeywordText("");
    setOpen(false);
    setKeywordAddingMode(false);
    setCurrentDescription(service.description);
    setDefaultSafetyImpactValue(service.service_safety_impact);
    setIsChanged(false);
    setIsImageChanged(false);
  };
  const handleClickOpen = () => {
    setOpen(true);
  };
  const handleDeleteKeyword = (item) => {
    const keywordsListCopy = JSON.parse(JSON.stringify(currentKeywordsList));
    const filteredKeywordsList = keywordsListCopy.filter((keyword) => keyword !== item);
    setCurrentKeywordsList(filteredKeywordsList);
  };

  const handleServiceNameSetting = (string) => {
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

  const handleKeywordSetting = (string) => {
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

  const handleDescriptionSetting = (string) => {
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

  const handleUpdatePTeamService = async () =>
    onSave(
      serviceName,
      imageFileData,
      imageDeleteFlag,
      currentKeywordsList,
      currentDescription,
      defaultSafetyImpactValue,
    );

  return (
    <>
      <IconButton onClick={handleClickOpen} sx={{ position: "absolute", right: 0, top: 0 }}>
        <SettingsIcon />
      </IconButton>
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="md">
        <DialogTitle flexGrow={1}>
          <Box alignItems="center" display="flex" flexDirection="row">
            <Typography flexGrow={1} className={dialogStyle.dialog_title}>
              Service settings
            </Typography>
            <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2}>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <FormLabel required>Name</FormLabel>
              <TextField
                required
                size="small"
                value={serviceName}
                placeholder={`Max length is ${maxServiceNameLengthInHalf} in half-width or ${Math.floor(maxServiceNameLengthInHalf / 2)} in full-width`}
                onChange={(e) => handleServiceNameSetting(e.target.value)}
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
                  setIsImageChanged={setIsImageChanged}
                  originalImage={image}
                />
              </Box>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column" }}>
              <FormLabel>Keywords (Max 5)</FormLabel>
              <Box>
                <Stack direction="row" spacing={1} useFlexGap sx={{ flexWrap: "wrap" }}>
                  {currentKeywordsList.map((keyword) => (
                    <Chip
                      key={keyword}
                      label={keyword}
                      onDelete={() => handleDeleteKeyword(keyword)}
                    />
                  ))}
                </Stack>
                {keywordAddingMode ? (
                  <Box sx={{ mt: 1 }}>
                    <TextField
                      variant="outlined"
                      size="small"
                      value={keywordText}
                      onChange={(e) => handleKeywordSetting(e.target.value)}
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
                        const updatedKeywordsList = [...currentKeywordsList, keywordText];
                        setCurrentKeywordsList(updatedKeywordsList);
                        setKeywordText("");
                        setKeywordAddingMode(false);
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
                    <Button
                      onClick={() => setKeywordAddingMode(!keywordAddingMode)}
                      disabled={currentKeywordsList.length >= maxKeywords}
                    >
                      + Add a new keyword
                    </Button>
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
                placeholder={`Max length is ${maxDescriptionLengthInHalf} in half-width or ${Math.floor(maxDescriptionLengthInHalf / 2)} in full-width`}
                value={currentDescription}
                onChange={(e) => handleDescriptionSetting(e.target.value)}
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
            disabled={!isChanged}
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
  image: PropTypes.string.isRequired,
  onSave: PropTypes.func.isRequired,
};
