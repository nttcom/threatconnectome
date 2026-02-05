import { ArrowDropDown as ArrowDropDownIcon } from "@mui/icons-material";
import { Button, ClickAwayListener, Grow, MenuItem, MenuList, Paper, Popper } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { CompleteTicketDialog } from "../../components/Ticket/CompleteTicketDialog";
import { ScheduleTicketDialog } from "../../components/Ticket/ScheduleTicketDialog";
import VulnDialogContext from "../../components/VulnDialogContext";
import { useUpdateTicketMutation } from "../../services/tcApi";
import { ticketHandlingStatusProps } from "../../utils/const";
import { errorToString } from "../../utils/func";

export function TicketHandlingStatusSelector(props) {
  const { pteamId, serviceId, vulnId, packageId, ticketId, currentStatus } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "TicketHandlingStatusSelector" });

  const [open, setOpen] = useState(false);
  const anchorRef = useRef(null);
  const [datepickerOpen, setDatepickerOpen] = useState(false);
  const [schedule, setSchedule] = useState(null); // Date object
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const [updateTicket] = useUpdateTicketMutation();

  const dateFormat = "yyyy/MM/dd HH:mm";
  const selectableItems = [
    {
      display: t("acknowledge"),
      rawStatus: "acknowledged",
      disabled: currentStatus.ticket_handling_status === "acknowledged",
    },
    { display: t("schedule"), rawStatus: "scheduled", disabled: false },
    {
      display: t("complete"),
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
    await updateTicket({
      path: { pteam_id: pteamId, ticket_id: ticketId },
      body: { ticket_status: { ...requestParams } },
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar(t("changeSucceeded"), { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(t("operationFailed", { error: errorToString(error) }), {
          variant: "error",
        }),
      );
  };

  const handleUpdateStatus = async (event, item) => {
    setOpen(false);
    switch (item.rawStatus) {
      case "completed":
        setCompleteDialogOpen(true);
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
      <VulnDialogContext value={{ vulnId }}>
        <CompleteTicketDialog
          pteamId={pteamId}
          serviceId={serviceId}
          packageId={packageId}
          ticketId={ticketId}
          onClose={() => setCompleteDialogOpen(false)}
          show={completeDialogOpen}
        />
      </VulnDialogContext>
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
      <ScheduleTicketDialog
        open={datepickerOpen}
        schedule={schedule}
        onClose={handleHideDatepicker}
        onSchedule={handleUpdateSchedule}
        onScheduleChange={setSchedule}
      />
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
};
