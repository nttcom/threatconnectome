import { ArrowDropDown as ArrowDropDownIcon } from "@mui/icons-material";
import { Button, ClickAwayListener, Grow, MenuItem, MenuList, Paper, Popper } from "@mui/material";
import { useSnackbar } from "notistack";
import { useRef, useState } from "react";
import type { MouseEvent as ReactMouseEvent } from "react";
import { useTranslation } from "react-i18next";

import type {
  TicketHandlingStatusType,
  TicketStatusRequest,
  TicketStatusResponse,
} from "../../../types/types.gen";
import { CompleteTicketDialog } from "../../components/Ticket/CompleteTicketDialog";
import { ScheduleTicketDialog } from "../../components/Ticket/ScheduleTicketDialog";
import VulnDialogContext from "../../components/VulnDialogContext";
import { useUpdateTicketMutation } from "../../services/tcApi";
import { ticketHandlingStatusProps } from "../../utils/const";
import { errorToString } from "../../utils/func";

type TicketHandlingStatusSelectorProps = {
  pteamId: string;
  serviceId: string;
  vulnId: string;
  packageVersionId?: string;
  ticketId: string;
  currentStatus: TicketStatusResponse;
};

type SelectableStatusItem = {
  display: string;
  rawStatus: Exclude<TicketHandlingStatusType, "alerted">;
  disabled: boolean;
};

export function TicketHandlingStatusSelector(props: TicketHandlingStatusSelectorProps) {
  const { pteamId, serviceId, vulnId, packageVersionId, ticketId, currentStatus } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "TicketHandlingStatusSelector" });

  const [open, setOpen] = useState(false);
  const anchorRef = useRef<HTMLButtonElement | null>(null);
  const [datepickerOpen, setDatepickerOpen] = useState(false);
  const [schedule, setSchedule] = useState<Date | null>(null);
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const [updateTicket] = useUpdateTicketMutation();

  const selectableItems: SelectableStatusItem[] = [
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

  const modifyTicketStatus = async (selectedStatus: TicketHandlingStatusType) => {
    const requestParams: TicketStatusRequest = { ticket_handling_status: selectedStatus };
    if (selectedStatus === "scheduled") {
      if (!schedule) return;
      requestParams.scheduled_at = schedule.toISOString();
    } else if (selectedStatus === "acknowledged") {
      requestParams.scheduled_at = null;
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

  const handleUpdateStatus = async (
    _event: ReactMouseEvent<HTMLElement>,
    item: SelectableStatusItem,
  ) => {
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

  const handleClose = (event: MouseEvent | TouchEvent) => {
    if (event.target instanceof Node && anchorRef.current?.contains(event.target)) return;
    setOpen(false);
  };

  if (!pteamId || !serviceId || !vulnId || !packageVersionId || !currentStatus) return <></>;

  const handleHideDatepicker = () => {
    setDatepickerOpen(false);
  };
  return (
    <>
      <VulnDialogContext value={{ vulnId }}>
        <CompleteTicketDialog
          pteamId={pteamId}
          serviceId={serviceId}
          packageVersionId={packageVersionId}
          ticketId={ticketId}
          originalNote={currentStatus.note || ""}
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
