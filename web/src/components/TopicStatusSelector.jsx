import { ArrowDropDown as ArrowDropDownIcon, Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  ClickAwayListener,
  Grow,
  IconButton,
  MenuItem,
  MenuList,
  Paper,
  Popper,
  TextField,
  Typography,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { isBefore } from "date-fns";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import dialogStyle from "../cssModule/dialog.module.css";
import {
  getTopicStatus,
  getPTeamServiceTaggedTicketIds,
  getPTeamServiceTagsSummary,
} from "../slices/pteam";
import { createTopicStatus } from "../utils/api";
import { topicStatusProps } from "../utils/const";
import { dateTimeFormat } from "../utils/func";

export function TopicStatusSelector(props) {
  const { pteamId, topicId, serviceId } = props;

  const [open, setOpen] = useState(false);
  const [selectableItems, setSelectableItems] = useState([]);
  const anchorRef = useRef(null);
  const [datepickerOpen, setDatepickerOpen] = useState(false);
  const [schedule, setSchedule] = useState(null); // Date object

  const { tagId } = useParams();
  const { enqueueSnackbar } = useSnackbar();

  const topicStatus = useSelector((state) => state.pteam.topicStatus); // dispatched by parent
  const topics = useSelector((state) => state.topics.topics); // dispatched by parent

  const dispatch = useDispatch();

  const dateFormat = "yyyy/MM/dd HH:mm";

  useEffect(() => {
    if (!pteamId || !topicId) return;
    if (!topicStatus[serviceId]?.[topicId]?.[tagId]) return; // resolved by parent
    const ttStatus = topicStatus[serviceId][topicId][tagId];
    const current = ttStatus.topic_status ?? "alerted";
    const items = [
      { display: "Acknowledge", rawStatus: "acknowledged", disabled: current === "acknowledged" },
      { display: "Schedule", rawStatus: "scheduled", disabled: false },
    ];
    setSelectableItems(items);
    setSchedule(
      ttStatus?.scheduled_at // scheduled_at(UTC) -> schedule(local)
        ? dateTimeFormat(ttStatus.scheduled_at)
        : null,
    );
  }, [tagId, pteamId, serviceId, topicId, topicStatus]);

  const modifyTopicStatus = async (selectedStatus) => {
    const ttStatus = topicStatus[serviceId][topicId][tagId];
    await createTopicStatus(pteamId, serviceId, topicId, tagId, {
      topic_status: selectedStatus,
      logging_ids: ttStatus.logging_ids ?? [],
      assignees: ttStatus.assignees ?? [],
      note: ttStatus.note,
      scheduled_at: selectedStatus === "scheduled" ? schedule.toISOString() : null,
    })
      .then(() => {
        if (selectedStatus !== ttStatus.topicStatus) {
          dispatch(
            getTopicStatus({
              pteamId: pteamId,
              serviceId: serviceId,
              topicId: topicId,
              tagId: tagId,
            }),
          );
          dispatch(getPTeamServiceTagsSummary({ pteamId: pteamId, serviceId: serviceId }));
        }
        if (ttStatus.topic_status === "completed") {
          dispatch(
            getPTeamServiceTaggedTicketIds({
              pteamId: pteamId,
              serviceId: serviceId,
              tagId: tagId,
            }),
          );
        }
        enqueueSnackbar("Change topic status succeeded", { variant: "success" });
      })
      .catch((error) => {
        const resp = error.response;
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" },
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
    if (!pteamId || !topicId || !topics[topicId] || !topicStatus[serviceId]?.[topicId]?.[tagId])
      return <></>;
    const ttStatus = topicStatus[serviceId][topicId][tagId];
    const currentStatus = ttStatus.topic_status ?? "alerted";

    const handleHideDatepicker = () => {
      setSchedule(ttStatus.scheduled_at ? dateTimeFormat(ttStatus.scheduled_at) : null);
      setDatepickerOpen(false);
    };
    const now = new Date();
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
        <Popper
          open={open}
          anchorEl={anchorRef.current}
          role={undefined}
          transition
          disablePortal
          sx={{ zIndex: 1 }}
        >
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
        <Dialog open={datepickerOpen} onClose={handleHideDatepicker} fullWidth>
          <DialogTitle>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Typography flexGrow={1} className={dialogStyle.dialog_title}>
                Set schedule
              </Typography>
              <IconButton onClick={handleHideDatepicker}>
                <CloseIcon />
              </IconButton>
            </Box>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 3 }}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateTimePicker
                  inputFormat={dateFormat}
                  label="Schedule Date (future date)"
                  mask="____/__/__ __:__"
                  minDateTime={now}
                  value={schedule}
                  onChange={(newDate) => setSchedule(newDate)}
                  renderInput={(params) => (
                    <TextField fullWidth margin="dense" required {...params} />
                  )}
                  sx={{ width: "100%" }}
                />
              </LocalizationProvider>
            </Box>
          </DialogContent>
          <DialogActions className={dialogStyle.action_area}>
            <Button
              onClick={handleUpdateSchedule}
              disabled={!isBefore(now, schedule)}
              className={dialogStyle.submit_btn}
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
  serviceId: PropTypes.string.isRequired,
};
