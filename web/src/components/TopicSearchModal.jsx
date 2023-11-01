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

export default function TopicSearchModal(props) {
  const { setShow, show } = props;

  const [startData, setStartData] = useState({});
  const [endData, setEndData] = useState({});
  const [adModeChange, setAdModeChange] = useState(false);
  const [dateFormList, setDateFormList] = useState("none");

  const advancedChange = (event) => {
    setAdModeChange(event.target.checked);
  };

  const searchModalClose = () => setShow(false);

  const now = moment();

  const dateFormChange = (event) => {
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
        <TextField variant="outlined" size="small" sx={{ width: "95%" }} />
      </Grid>
    </Grid>
  );

  const mispForm = (
    <Grid container sx={{ margin: 1.5 }}>
      <Grid item xs={2} md={2}>
        <Typography sx={{ marginTop: "10px" }}>MISP Tag</Typography>
      </Grid>
      <Grid item xs={10} md={10}>
        <TextField variant="outlined" size="small" sx={{ width: "95%" }} />
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
            <MenuItem value="today">Last 24h</MenuItem>
            <MenuItem value="week">Last 7days</MenuItem>
            <MenuItem value="range">Date Range</MenuItem>
            <MenuItem value="since">Since</MenuItem>
            <MenuItem value="until">Until</MenuItem>
          </Select>
        </FormControl>
        {(dateFormList === "since" || dateFormList === "until") && (
          <Grid item xs={5}>
            <LocalizationProvider dateAdapter={AdapterMoment}>
              <DateTimePicker
                inputFormat="YYYY/MM/DD HH:mm"
                mask="____/__/__ __:__"
                minDateTime={now}
                onChange={(moment) =>
                  setStartData({ ...startData, expiration: moment ? moment.toDate() : "" })
                }
                renderInput={(params) => (
                  <TextField fullWidth margin="dense" required {...params} />
                )}
                value={startData.expiration}
              />
            </LocalizationProvider>
          </Grid>
        )}

        {dateFormList === "range" && (
          <Grid item xs={11.4} display="flex">
            <LocalizationProvider dateAdapter={AdapterMoment}>
              <DateTimePicker
                inputFormat="YYYY/MM/DD HH:mm"
                mask="____/__/__ __:__"
                minDateTime={now}
                onChange={(moment) =>
                  setStartData({ ...startData, expiration: moment ? moment.toDate() : "" })
                }
                renderInput={(params) => (
                  <TextField fullWidth margin="dense" required {...params} />
                )}
                value={startData.expiration}
              />
            </LocalizationProvider>
            <Typography sx={{ margin: "20px" }}>~</Typography>
            <LocalizationProvider dateAdapter={AdapterMoment}>
              <DateTimePicker
                inputFormat="YYYY/MM/DD HH:mm"
                mask="____/__/__ __:__"
                minDateTime={now}
                onChange={(moment) =>
                  setEndData({ ...endData, expiration: moment ? moment.toDate() : "" })
                }
                renderInput={(params) => (
                  <TextField fullWidth margin="dense" required {...params} />
                )}
                value={endData.expiration}
              />
            </LocalizationProvider>
          </Grid>
        )}
      </Grid>
    </Grid>
  );

  const createrForm = (
    <Grid container sx={{ margin: 1.5 }}>
      <Grid item xs={2} md={2}>
        <Typography sx={{ marginTop: "10px" }}>Creater ID</Typography>
      </Grid>
      <Grid item xs={10} md={10}>
        <TextField variant="outlined" size="small" sx={{ width: "95%" }} />
      </Grid>
    </Grid>
  );

  const uuidForm = (
    <Grid container sx={{ margin: 1.5 }}>
      <Grid item xs={2} md={2}>
        <Typography sx={{ marginTop: "10px" }}>UUID</Typography>
      </Grid>
      <Grid item xs={10} md={10}>
        <TextField variant="outlined" size="small" sx={{ width: "95%" }} />
      </Grid>
    </Grid>
  );

  return (
    <>
      <Dialog onClose={searchModalClose} open={show} PaperProps={{ sx: { width: 700 } }}>
        <>
          <DialogTitle>
            <Box alignItems="center" display="flex" flexDirection="row" sx={{ mb: -3 }}>
              <Typography flexGrow={1} variant="inherit" sx={{ fontWeight: 900 }}>
                Topic Search
              </Typography>
              <IconButton onClick={() => setShow(false)} sx={{ color: grey[500] }}>
                <CloseIcon />
              </IconButton>
            </Box>
          </DialogTitle>
          <DialogContent>
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
                {createrForm}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Box display="flex">
              <Button
                variant="contained"
                color="success"
                sx={{ margin: 1, textTransform: "none" }}
                onClick={() => setShow(false)}
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
  setShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
};
