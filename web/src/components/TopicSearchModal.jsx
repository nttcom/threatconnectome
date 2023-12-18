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
  Switch,
  FormControl,
  Select,
  MenuItem,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterMoment } from "@mui/x-date-pickers/AdapterMoment";
import moment from "moment";
import PropTypes from "prop-types";
import React, { useState } from "react";

export function TopicSearchModal(props) {
  const { show, onSearch, onCancel } = props;

  const [titleWords, setTitleWords] = useState("");
  const [mispTags, setMispTags] = useState("");
  const [creatorIds, setCreatorIds] = useState("");
  const [topicIds, setTopicIds] = useState("");
  const [updatedAfter, setUpdatedAfter] = useState(null); // moment object
  const [updatedBefore, setUpdatedBefore] = useState(null); // moment object
  const [adModeChange, setAdModeChange] = useState(false);
  const [dateFormList, setDateFormList] = useState("");

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
      updatedAfter: updatedAfter?.utc?.().toDate(),
      updatedBefore: updatedBefore?.utc?.().toDate(),
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
        setUpdatedAfter(moment().add(-1, "days"));
        break;
      case "in7days":
        setUpdatedAfter(moment().add(-7, "days"));
        break;
      default:
        break;
    }
    setDateFormList(event.target.value);
  };

  const Android12Switch = styled(Switch)(({ theme }) => ({
    padding: 8,
    "& .MuiSwitch-track": {
      borderRadius: 22 / 2,
      "&:before, &:after": {
        content: "''",
        position: "absolute",
        top: "50%",
        transform: "translateY(-50%)",
        width: 16,
        height: 16,
      },
      "&:before": {
        backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
          theme.palette.getContrastText(theme.palette.primary.main)
        )}" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>")`,
        left: 12,
      },
      "&:after": {
        backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
          theme.palette.getContrastText(theme.palette.primary.main)
        )}" d="M19,13H5V11H19V13Z" /></svg>")`,
        right: 12,
      },
    },
    "& .MuiSwitch-thumb": {
      boxShadow: "none",
      width: 16,
      height: 16,
      margin: 2,
    },
  }));

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
              inputFormat="YYYY/MM/DD HH:mm"
              mask="____/__/__ __:__"
              maxDateTime={moment()}
              value={dateFormList === "since" ? updatedAfter : updatedBefore}
              onChange={(moment) =>
                (dateFormList === "since" ? setUpdatedAfter : setUpdatedBefore)(moment)
              }
              renderInput={(params) => <TextField fullWidth margin="dense" required {...params} />}
            />
          </Grid>
        )}
        {dateFormList === "range" && (
          <Grid item xs={11.4} display="flex">
            <DateTimePicker
              inputFormat="YYYY/MM/DD HH:mm"
              mask="____/__/__ __:__"
              maxDateTime={updatedBefore || moment()}
              value={updatedAfter}
              onChange={(moment) => setUpdatedAfter(moment)}
              renderInput={(params) => <TextField fullWidth margin="dense" required {...params} />}
            />
            <Typography sx={{ margin: "20px" }}>~</Typography>
            <DateTimePicker
              inputFormat="YYYY/MM/DD HH:mm"
              mask="____/__/__ __:__"
              minDateTime={updatedAfter}
              maxDateTime={moment()}
              value={updatedBefore}
              onChange={(moment) => setUpdatedBefore(moment)}
              renderInput={(params) => <TextField fullWidth margin="dense" required {...params} />}
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
        <>
          <DialogTitle>
            <Box alignItems="center" display="flex" flexDirection="row" sx={{ mb: -3 }}>
              <Typography flexGrow={1} variant="inherit" sx={{ fontWeight: 900 }}>
                Topic Search
              </Typography>
              <IconButton onClick={handleCancel} sx={{ color: grey[500] }}>
                <CloseIcon />
              </IconButton>
            </Box>
          </DialogTitle>
          <DialogContent>
            <LocalizationProvider dateAdapter={AdapterMoment}>
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
          <DialogActions>
            <Box display="flex">
              <Button
                variant="contained"
                color="success"
                sx={{ margin: 1, textTransform: "none" }}
                onClick={handleSearch}
              >
                Search
              </Button>
            </Box>
          </DialogActions>
        </>
      </Dialog>
    </>
  );
}
TopicSearchModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onSearch: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};
