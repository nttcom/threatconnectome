import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControlLabel,
  IconButton,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  Grid,
  FormControl,
  Select,
  MenuItem,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { addDays } from "date-fns";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { Android12Switch } from "../../components/Android12Switch";
import dialogStyle from "../../cssModule/dialog.module.css";
import { cvssRatings, cvssConvertToScore } from "../../utils/cvssUtils";
import { isValidCVEFormat } from "../../utils/vulnUtils";

export function VulnSearchModal(props) {
  const { t } = useTranslation("vulnManagement", { keyPrefix: "VulnSearchModal" });
  const { show, onSearch, onCancel } = props;

  const [titleWords, setTitleWords] = useState("");
  const [cveIds, setCveIds] = useState("");
  const [creatorIds, setCreatorIds] = useState("");
  const [vulnIds, setVulnIds] = useState("");
  const [updatedAfter, setUpdatedAfter] = useState(null); // Date object
  const [updatedBefore, setUpdatedBefore] = useState(null); // Date object
  const [adModeChange, setAdModeChange] = useState(false);
  const [dateFormList, setDateFormList] = useState("");
  const [cvssName, setCvssName] = useState("");
  const [minCvssScore, setMinCvssScore] = useState("");
  const [maxCvssScore, setMaxCvssScore] = useState("");
  const { enqueueSnackbar } = useSnackbar();

  const now = new Date();
  const cvssRatingsKeys = Object.keys(cvssRatings);

  const advancedChange = (event) => {
    setAdModeChange(event.target.checked);
    if (!event.target.checked) clearAdvancedParams(); // clear on close
  };

  const handleCancel = () => {
    onCancel();
    clearAllParams();
  };

  const handleSearch = () => {
    const trimmedCveIds = cveIds.trim();
    if (trimmedCveIds && !isValidCVEFormat(trimmedCveIds)) {
      enqueueSnackbar(t("invalidCveFormat"), {
        variant: "error",
      });
      return;
    }
    const params = {
      titleWords: titleWords,
      cveIds: trimmedCveIds,
      vulnIds: vulnIds,
      creatorIds: creatorIds,
      updatedAfter: updatedAfter?.toISOString(),
      updatedBefore: updatedBefore?.toISOString(),
      minCvssV3Score: minCvssScore,
      maxCvssV3Score: maxCvssScore,
    };
    onSearch(params);
    clearAllParams();
  };

  const clearAdvancedParams = () => {
    setCreatorIds("");
    setVulnIds("");
    setUpdatedAfter(null);
    setUpdatedBefore(null);
    setDateFormList("");
    setCvssName("");
    setMinCvssScore("");
    setMaxCvssScore("");
  };

  const clearAllParams = () => {
    setTitleWords("");
    setCveIds("");
    clearAdvancedParams();
  };

  const dateFormChange = (event) => {
    setUpdatedBefore(null);
    switch (event.target.value) {
      case "":
      case "range":
      case "since":
      case "until":
        setUpdatedAfter(null);
        break;
      case "in24hours":
        setUpdatedAfter(addDays(now, -1));
        break;
      case "in7days":
        setUpdatedAfter(addDays(now, -7));
        break;
      default:
        break;
    }
    setDateFormList(event.target.value);
  };

  const handleCvssName = (event, newCvssName) => {
    setCvssName(newCvssName);
    const score = cvssConvertToScore(newCvssName);
    setMinCvssScore(score[0]);
    setMaxCvssScore(score[1]);
  };

  const handleMinCvssScore = (event) => {
    setCvssName("");
    setMinCvssScore(event.target.value);
  };

  const handleMaxCvssScore = (event) => {
    setCvssName("");
    setMaxCvssScore(event.target.value);
  };

  const isValidCvssScore = (cvssScore) => {
    const regex = /^\d+(\.\d{1})?$/; // Regular expression to allow only numbers to one decimal place
    return (regex.test(cvssScore) && 0 <= cvssScore && cvssScore <= 10) || cvssScore === "";
  };

  const isValidUserInput = isValidCvssScore(minCvssScore) && isValidCvssScore(maxCvssScore);

  const titleForm = (
    <Grid container sx={{ margin: 1.5, width: "100%" }}>
      <Grid size={{ xs: 2, md: 2 }}>
        <Typography sx={{ marginTop: "10px" }}>{t("titleLabel")}</Typography>
      </Grid>
      <Grid size={{ xs: 10, md: 10 }} sx={{ display: "flex" }}>
        <TextField
          value={titleWords}
          onChange={(event) => setTitleWords(event.target.value)}
          variant="outlined"
          size="small"
          sx={{ width: "95%" }}
        />
      </Grid>
    </Grid>
  );

  const cveIdForm = (
    <Grid container sx={{ margin: 1.5, width: "100%" }}>
      <Grid size={{ xs: 2, md: 2 }}>
        <Typography sx={{ marginTop: "10px" }}>{t("cveIdLabel")}</Typography>
      </Grid>
      <Grid size={{ xs: 10, md: 10 }}>
        <TextField
          value={cveIds}
          onChange={(event) => setCveIds(event.target.value)}
          variant="outlined"
          size="small"
          sx={{ width: "95%" }}
        />
      </Grid>
    </Grid>
  );

  const cvssForm = (
    <Grid container sx={{ margin: 1.5, width: "100%" }} alignItems={"center"}>
      <Grid size={{ xs: 2, md: 2 }}>
        <Typography sx={{ marginTop: "10px" }}>{t("cvssV3Label")}</Typography>
      </Grid>
      <Grid size={{ xs: 10, md: 10 }}>
        <ToggleButtonGroup
          color="primary"
          exclusive
          value={cvssName}
          onChange={handleCvssName}
          sx={{ width: "95%" }}
          fullWidth
        >
          {cvssRatingsKeys.map((cvssRatingKey) => (
            <ToggleButton key={cvssRatingKey} value={cvssRatingKey}>
              {cvssRatingKey}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
        <Box display="flex" flexDirection="row" sx={{ mt: 2 }}>
          <TextField
            value={minCvssScore}
            onChange={handleMinCvssScore}
            variant="outlined"
            size="small"
            sx={{ width: "40%" }}
          />
          <Box display="flex" alignItems="center" justifyContent="center" sx={{ width: "15%" }}>
            <Divider orientation="horizontal" sx={{ borderColor: "black", width: "20%" }} />
          </Box>
          <TextField
            value={maxCvssScore}
            onChange={handleMaxCvssScore}
            variant="outlined"
            size="small"
            sx={{ width: "40%" }}
          />
        </Box>
      </Grid>
    </Grid>
  );

  const dateForm = (
    <Grid container sx={{ margin: 1.5, width: "100%" }}>
      <Grid size={{ xs: 2, md: 2 }}>
        <Typography sx={{ marginTop: "10px" }}>{t("lastUpdateLabel")}</Typography>
      </Grid>
      <Grid size={{ xs: 10, md: 10 }} display="flex" flexDirection="column">
        <FormControl variant="standard" sx={{ m: 1, maxWidth: 200 }}>
          <Select value={dateFormList} onChange={dateFormChange}>
            <MenuItem value="">{t("none")}</MenuItem>
            <MenuItem value="in24hours">{t("last24h")}</MenuItem>
            <MenuItem value="in7days">{t("last7days")}</MenuItem>
            <MenuItem value="range">{t("dateRange")}</MenuItem>
            <MenuItem value="since">{t("since")}</MenuItem>
            <MenuItem value="until">{t("until")}</MenuItem>
          </Select>
        </FormControl>
        {(dateFormList === "since" || dateFormList === "until") && (
          <Grid size={{ xs: 5 }}>
            <DateTimePicker
              format="yyyy/MM/dd HH:mm"
              mask="____/__/__ __:__"
              maxDateTime={now}
              value={dateFormList === "since" ? updatedAfter : updatedBefore}
              onChange={(newDate) =>
                (dateFormList === "since" ? setUpdatedAfter : setUpdatedBefore)(newDate)
              }
              slotProps={{
                textField: { size: "small", fullWidth: true, margin: "dense", required: true },
              }}
            />
          </Grid>
        )}
        {dateFormList === "range" && (
          <Grid size={{ xs: 11.4 }} display="flex">
            <DateTimePicker
              inputFormat="yyyy/MM/dd HH:mm"
              mask="____/__/__ __:__"
              maxDateTime={updatedBefore || now}
              value={updatedAfter}
              onChange={(newDate) => setUpdatedAfter(newDate)}
              slotProps={{
                textField: { size: "small", fullWidth: true, margin: "dense", required: true },
              }}
            />
            <Typography sx={{ margin: "20px" }}>~</Typography>
            <DateTimePicker
              inputFormat="yyyy/MM/dd HH:mm"
              mask="____/__/__ __:__"
              minDateTime={updatedAfter}
              maxDateTime={now}
              value={updatedBefore}
              onChange={(newDate) => setUpdatedBefore(newDate)}
              slotProps={{
                textField: { size: "small", fullWidth: true, margin: "dense", required: true },
              }}
            />
          </Grid>
        )}
      </Grid>
    </Grid>
  );

  const creatorForm = (
    <Grid container sx={{ margin: 1.5, width: "100%" }}>
      <Grid size={{ xs: 2, md: 2 }}>
        <Typography sx={{ marginTop: "10px" }}>{t("creatorIdLabel")}</Typography>
      </Grid>
      <Grid size={{ xs: 10, md: 10 }}>
        <TextField
          value={creatorIds}
          onChange={(event) => setCreatorIds(event.target.value)}
          variant="outlined"
          size="small"
          sx={{ width: "95%" }}
        />
      </Grid>
    </Grid>
  );

  const uuidForm = (
    <Grid container sx={{ margin: 1.5, width: "100%" }}>
      <Grid size={{ xs: 2, md: 2 }}>
        <Typography sx={{ marginTop: "10px" }}>{t("vulnIdLabel")}</Typography>
      </Grid>
      <Grid size={{ xs: 10, md: 10 }}>
        <TextField
          value={vulnIds}
          onChange={(event) => setVulnIds(event.target.value)}
          variant="outlined"
          size="small"
          sx={{ width: "95%" }}
        />
      </Grid>
    </Grid>
  );

  return (
    <>
      <Dialog onClose={handleCancel} open={show} PaperProps={{ sx: { width: 700 } }}>
        <DialogTitle>
          <Box alignItems="center" display="flex" flexDirection="row" sx={{ mb: -3 }}>
            <Typography flexGrow={1} className={dialogStyle.dialog_title}>
              {t("title")}
            </Typography>
            <IconButton onClick={handleCancel}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box display="flex" flexDirection="row-reverse" sx={{ marginTop: 0 }}>
              <FormControlLabel
                control={<Android12Switch checked={adModeChange} onChange={advancedChange} />}
                label={t("advancedMode")}
              />
            </Box>
            {titleForm}
            {cveIdForm}
            {adModeChange && (
              <Box>
                {cvssForm}
                {dateForm}
                {uuidForm}
                {creatorForm}
              </Box>
            )}
          </LocalizationProvider>
        </DialogContent>
        <DialogActions className={dialogStyle.action_area}>
          <Box display="flex">
            <Button
              className={dialogStyle.submit_btn}
              onClick={handleSearch}
              disabled={!isValidUserInput}
            >
              {t("search")}
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </>
  );
}
VulnSearchModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onSearch: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};
