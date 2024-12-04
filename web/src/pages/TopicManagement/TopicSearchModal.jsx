import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  TextField,
  Typography,
  Grid,
  FormControl,
  Select,
  MenuItem,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { addDays } from "date-fns";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { Android12Switch } from "../../components/Android12Switch";
import dialogStyle from "../../cssModule/dialog.module.css";

export function TopicSearchModal(props) {
  const { show, onSearch, onCancel } = props;

  const [titleWords, setTitleWords] = useState("");
  const [mispTags, setMispTags] = useState("");
  const [creatorIds, setCreatorIds] = useState("");
  const [topicIds, setTopicIds] = useState("");
  const [updatedAfter, setUpdatedAfter] = useState(null); // Date object
  const [updatedBefore, setUpdatedBefore] = useState(null); // Date object
  const [adModeChange, setAdModeChange] = useState(false);
  const [dateFormList, setDateFormList] = useState("");

  const now = new Date();

  const advancedChange = (event) => {
    setAdModeChange(event.target.checked);
    if (!event.target.checked) clearAdvancedParams(); // clear on close
  };

  const handleCancel = () => {
    onCancel();
    clearAllParams();
  };

  const handleSearch = () => {
    const params = {
      titleWords: titleWords,
      mispTags: mispTags,
      topicIds: topicIds,
      creatorIds: creatorIds,
      updatedAfter: updatedAfter?.toISOString(),
      updatedBefore: updatedBefore?.toISOString(),
    };
    onSearch(params);
    clearAllParams();
  };

  const clearAdvancedParams = () => {
    setCreatorIds("");
    setTopicIds("");
    setUpdatedAfter(null);
    setUpdatedBefore(null);
    setDateFormList("");
  };

  const clearAllParams = () => {
    setTitleWords("");
    setMispTags("");
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

  const titleForm = (
    <Grid container sx={{ margin: 1.5, width: "100%" }}>
      <Grid item xs={2} md={2}>
        <Typography sx={{ marginTop: "10px" }}>Title</Typography>
      </Grid>
      <Grid item xs={10} md={10} sx={{ display: "flex" }}>
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

  const mispForm = (
    <Grid container sx={{ margin: 1.5 }}>
      <Grid item xs={2} md={2}>
        <Typography sx={{ marginTop: "10px" }}>MISP Tag</Typography>
      </Grid>
      <Grid item xs={10} md={10}>
        <TextField
          value={mispTags}
          onChange={(event) => setMispTags(event.target.value)}
          variant="outlined"
          size="small"
          sx={{ width: "95%" }}
        />
      </Grid>
    </Grid>
  );

  const dateForm = (
    <Grid container sx={{ margin: 1.5 }}>
      <Grid item xs={2} md={2}>
        <Typography sx={{ marginTop: "10px" }}>Last Update</Typography>
      </Grid>
      <Grid item xs={10} md={10} display="flex" flexDirection="column">
        <FormControl variant="standard" sx={{ m: 1, maxWidth: 200 }}>
          <Select value={dateFormList} onChange={dateFormChange}>
            <MenuItem value="">None</MenuItem>
            <MenuItem value="in24hours">Last 24h</MenuItem>
            <MenuItem value="in7days">Last 7days</MenuItem>
            <MenuItem value="range">Date Range</MenuItem>
            <MenuItem value="since">Since</MenuItem>
            <MenuItem value="until">Until</MenuItem>
          </Select>
        </FormControl>
        {(dateFormList === "since" || dateFormList === "until") && (
          <Grid item xs={5}>
            <DateTimePicker
              inputFormat="yyyy/MM/dd HH:mm"
              mask="____/__/__ __:__"
              maxDateTime={now}
              value={dateFormList === "since" ? updatedAfter : updatedBefore}
              onChange={(newDate) =>
                (dateFormList === "since" ? setUpdatedAfter : setUpdatedBefore)(newDate)
              }
              renderInput={(params) => (
                <TextField size="small" fullWidth margin="dense" required {...params} />
              )}
            />
          </Grid>
        )}
        {dateFormList === "range" && (
          <Grid item xs={11.4} display="flex">
            <DateTimePicker
              inputFormat="yyyy/MM/dd HH:mm"
              mask="____/__/__ __:__"
              maxDateTime={updatedBefore || now}
              value={updatedAfter}
              onChange={(newDate) => setUpdatedAfter(newDate)}
              renderInput={(params) => (
                <TextField size="small" fullWidth margin="dense" required {...params} />
              )}
            />
            <Typography sx={{ margin: "20px" }}>~</Typography>
            <DateTimePicker
              inputFormat="yyyy/MM/dd HH:mm"
              mask="____/__/__ __:__"
              minDateTime={updatedAfter}
              maxDateTime={now}
              value={updatedBefore}
              onChange={(newDate) => setUpdatedBefore(newDate)}
              renderInput={(params) => (
                <TextField size="small" fullWidth margin="dense" required {...params} />
              )}
            />
          </Grid>
        )}
      </Grid>
    </Grid>
  );

  const creatorForm = (
    <Grid container sx={{ margin: 1.5 }}>
      <Grid item xs={2} md={2}>
        <Typography sx={{ marginTop: "10px" }}>Creator ID</Typography>
      </Grid>
      <Grid item xs={10} md={10}>
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
    <Grid container sx={{ margin: 1.5 }}>
      <Grid item xs={2} md={2}>
        <Typography sx={{ marginTop: "10px" }}>Topic ID</Typography>
      </Grid>
      <Grid item xs={10} md={10}>
        <TextField
          value={topicIds}
          onChange={(event) => setTopicIds(event.target.value)}
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
              Topic Search
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
                label="Advanced Mode"
              />
            </Box>
            {titleForm}
            {mispForm}
            {adModeChange && (
              <Box>
                {dateForm}
                {uuidForm}
                {creatorForm}
              </Box>
            )}
          </LocalizationProvider>
        </DialogContent>
        <DialogActions className={dialogStyle.action_area}>
          <Box display="flex">
            <Button className={dialogStyle.submit_btn} onClick={handleSearch}>
              Search
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </>
  );
}
TopicSearchModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onSearch: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};
