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
import { useRef, useState } from "react";

import dialogStyle from "../../../cssModule/dialog.module.css";
import { useUpdateTicketMutation } from "../../../services/tcApi";
import { ticketHandlingStatusProps } from "../../../utils/const";
import { errorToString } from "../../../utils/func";

import { ReportCompletedActions } from "./ReportCompletedActions";

export function TicketHandlingStatusSelector(props) {
  const { pteamId, serviceId, vulnId, packageId, ticketId, currentStatus, updateAction } = props;

  const [open, setOpen] = useState(false);
  const anchorRef = useRef(null);
  const [datepickerOpen, setDatepickerOpen] = useState(false);
  const [schedule, setSchedule] = useState(null); // Date object
  const [actionModalOpen, setActionModalOpen] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const [updateTicket] = useUpdateTicketMutation();

  const dateFormat = "yyyy/MM/dd HH:mm";
  const selectableItems = [
    {
      display: "Acknowledge",
      rawStatus: "acknowledged",
      disabled: currentStatus.ticket_handling_status === "acknowledged",
    },
    { display: "Schedule", rawStatus: "scheduled", disabled: false },
    {
      display: "Complete",
      rawStatus: "completed",
      disabled: currentStatus.ticket_handling_status === "completed",
    },
  ];

  const modifyTicketStatus = async (selectedStatus) => {
    let requestParams = { ticket_handling_status: selectedStatus };
    if (selectedStatus === "scheduled") {
      if (!schedule) return;
      requestParams["scheduled_at"] = schedule.toISOString();
    } else if (selectedStatus === "acknowledged") {
      requestParams["scheduled_at"] = null;
    }
    await updateTicket({ pteamId, ticketId, data: { ticket_status: { ...requestParams } } })
      .unwrap()
      .then(() => {
        enqueueSnackbar("Change ticket status succeeded", { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" }),
      );
  };

  const handleUpdateStatus = async (event, item) => {
    setOpen(false);
    switch (item.rawStatus) {
      case "completed":
        setActionModalOpen(true);
        return;
      case "scheduled":
        setDatepickerOpen(true);
        return;
      default:
        break;
    }
    modifyTicketStatus(item.rawStatus);
  };

  const handleUpdateSchedule = async () => {
    setDatepickerOpen(false);
    modifyTicketStatus("scheduled");
  };

  const handleClose = (event) => {
    if (anchorRef.current?.contains(event.target)) return;
    setOpen(false);
  };

  if (!pteamId || !serviceId || !vulnId || !packageId || !currentStatus) return <></>;

  const handleHideDatepicker = () => {
    setDatepickerOpen(false);
  };
  const now = new Date();

  return (
    <>
      <ReportCompletedActions
        pteamId={pteamId}
        serviceId={serviceId}
        ticketId={ticketId}
        vulnId={vulnId}
        packageId={packageId}
        updateAction={updateAction}
        onSetShow={setActionModalOpen}
        show={actionModalOpen}
      />
      <Button
        endIcon={<ArrowDropDownIcon />}
        sx={{
          ...ticketHandlingStatusProps[currentStatus.ticket_handling_status].buttonStyle,
          fontSize: 14,
          padding: "1px 3px",
          minHeight: "25px",
          maxHeight: "25px",
          textTransform: "none",
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
        {ticketHandlingStatusProps[currentStatus.ticket_handling_status].chipLabelCapitalized}
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
                      selected={currentStatus.ticket_handling_status === item.rawStatus}
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
}

TicketHandlingStatusSelector.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  ticketId: PropTypes.string.isRequired,
  currentStatus: PropTypes.object.isRequired,
  updateAction: PropTypes.object.isRequired,
};
