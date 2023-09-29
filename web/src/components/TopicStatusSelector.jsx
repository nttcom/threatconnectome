import { ArrowDropDown as ArrowDropDownIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  ClickAwayListener,
  Grow,
  MenuItem,
  MenuList,
  Paper,
  Popper,
  TextField,
  Typography,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterMoment } from "@mui/x-date-pickers/AdapterMoment";
import moment from "moment";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import {
  getPTeamSolvedTaggedTopicIds,
  getPTeamTagsSummary,
  getPTeamTopicStatus,
  getPTeamUnsolvedTaggedTopicIds,
} from "../slices/pteam";
import { createTopicStatus } from "../utils/api";
import { topicStatusProps } from "../utils/const";
import { dateTimeFormat } from "../utils/func";

export default function TopicStatusSelector(props) {
  const { pteamId, topicId } = props;

  const [open, setOpen] = useState(false);
  const [selectableItems, setSelectableItems] = useState([]);
  const anchorRef = useRef(null);
  const [datepickerOpen, setDatepickerOpen] = useState(false);
  const [schedule, setSchedule] = useState(null); // local time string (or null)

  const { tagId } = useParams();
  const { enqueueSnackbar } = useSnackbar();

  const topicStatus = useSelector((state) => state.pteam.topicStatus); // dispatched by parent
  const topics = useSelector((state) => state.topics); // dispatched by parent

  const dispatch = useDispatch();

  const dateFormat = "YYYY/MM/DD HH:mm";

  useEffect(() => {
    if (!pteamId || !topicId) return;
    if (!topicStatus[topicId]?.[tagId]) return; // resolved by parent
    const ttStatus = topicStatus[topicId][tagId];
    const current = ttStatus.topic_status ?? "alerted";
    const items = [
      { display: "Acknowledge", rawStatus: "acknowledged", disabled: current === "acknowledged" },
      { display: "Schedule", rawStatus: "scheduled", disabled: false },
    ];
    setSelectableItems(items);
    setSchedule(
      ttStatus?.scheduled_at // scheduled_at(UTC) -> schedule(local)
        ? dateTimeFormat(ttStatus.scheduled_at)
        : null
    );
  }, [tagId, pteamId, topicId, topicStatus]);

  const modifyTopicStatus = async (selectedStatus) => {
    const ttStatus = topicStatus[topicId][tagId];
    await createTopicStatus(pteamId, topicId, tagId, {
      topic_status: selectedStatus,
      logging_ids: ttStatus.logging_ids ?? [],
      assignees: ttStatus.assignees ?? [],
      note: ttStatus.note,
      scheduled_at:
        selectedStatus === "scheduled"
          ? moment(schedule ?? "", dateFormat)
              .utc()
              .toISOString()
          : null,
    })
      .then(() => {
        if (selectedStatus !== ttStatus.topicStatus) {
          dispatch(getPTeamTopicStatus({ pteamId: pteamId, topicId: topicId, tagId: tagId }));
          dispatch(getPTeamTagsSummary(pteamId));
        }
        if (ttStatus.topic_status === "completed") {
          dispatch(getPTeamSolvedTaggedTopicIds({ pteamId: pteamId, tagId: tagId }));
          dispatch(getPTeamUnsolvedTaggedTopicIds({ pteamId: pteamId, tagId: tagId }));
        }
        enqueueSnackbar("Change topic status succeeded", { variant: "success" });
      })
      .catch((error) => {
        const resp = error.response;
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" }
        );
      });
  };

  const handleUpdateStatus = async (event, item) => {
    setOpen(false);
    if (item.rawStatus === "scheduled") {
      setDatepickerOpen(true);
      return;
    }
    modifyTopicStatus(item.rawStatus);
  };

  const handleUpdateSchedule = async () => {
    setDatepickerOpen(false);
    modifyTopicStatus("scheduled");
  };

  const handleClose = (event) => {
    if (anchorRef.current?.contains(event.target)) return;
    setOpen(false);
  };

  return (() => {
    if (!pteamId || !topicId || !topics[topicId] || !topicStatus[topicId]?.[tagId]) return <></>;
    const ttStatus = topicStatus[topicId][tagId];
    const currentStatus = ttStatus.topic_status ?? "alerted";

    const handleHideDatepicker = () => {
      setSchedule(ttStatus.scheduled_at ? dateTimeFormat(ttStatus.scheduled_at) : null);
      setDatepickerOpen(false);
    };
    const now = moment();
    return (
      <>
        <Button
          endIcon={<ArrowDropDownIcon />}
          sx={{
            ...topicStatusProps[currentStatus].buttonStyle,
            fontSize: 12,
            padding: "1px 3px",
            minHeight: "25px",
            maxHeight: "25px",
            textTransform: "none",
            fontWeight: 900,
            borderStyle: "none",
            mr: 1,
            "&:hover": {
              borderStyle: "none",
            },
          }}
          aria-controls={open ? "status-menu" : undefined}
          aria-expanded={open ? "true" : undefined}
          aria-haspopup="menu"
          onClick={() => setOpen(!open)}
          ref={anchorRef}
        >
          {topicStatusProps[currentStatus].chipLabelCapitalized}
        </Button>
        <Popper open={open} anchorEl={anchorRef.current} role={undefined} transition disablePortal>
          {({ TransitionProps, placement }) => (
            <Grow
              {...TransitionProps}
              style={{
                transformOrigin: placement === "bottom" ? "center top" : "center bottom",
              }}
            >
              <Paper>
                <ClickAwayListener onClickAway={handleClose}>
                  <MenuList autoFocusItem>
                    {selectableItems.map((item) => (
                      <MenuItem
                        key={item.rawStatus}
                        selected={ttStatus?.topic_status === item.rawStatus}
                        disabled={item.disabled}
                        onClick={(event) => handleUpdateStatus(event, item)}
                        dense={true}
                      >
                        {item.display}
                      </MenuItem>
                    ))}
                  </MenuList>
                </ClickAwayListener>
              </Paper>
            </Grow>
          )}
        </Popper>
        <Dialog onClose={handleHideDatepicker} open={datepickerOpen}>
          <DialogTitle>
            <Box alignItems="center" display="flex" flexGrow={1}>
              <Typography flexGrow={1} variant="inherit">
                Set schedule
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent>
            <LocalizationProvider dateAdapter={AdapterMoment}>
              <DateTimePicker
                inputFormat={dateFormat}
                label="Schedule Date (future date)"
                mask="____/__/__ __:__"
                minDateTime={now}
                onChange={(moment) => setSchedule(moment ? moment.toDate() : "")}
                renderInput={(params) => (
                  <TextField fullWidth margin="dense" required {...params} />
                )}
                value={schedule}
              />
            </LocalizationProvider>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleHideDatepicker}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleUpdateSchedule}
              disabled={!now.isBefore(schedule)}
            >
              Schedule
            </Button>
          </DialogActions>
        </Dialog>
      </>
    );
  })();
}

TopicStatusSelector.propTypes = {
  pteamId: PropTypes.string.isRequired,
  topicId: PropTypes.string.isRequired,
};
