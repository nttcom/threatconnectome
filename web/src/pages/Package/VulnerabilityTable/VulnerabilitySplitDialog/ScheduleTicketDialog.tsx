import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { isBefore } from "date-fns";

type ScheduleTicketDialogProps = {
  open: boolean;
  schedule: Date | null;
  onClose: () => void;
  onSchedule: () => void;
  onScheduleChange: (date: Date | null) => void;
  isLoading?: boolean;
};

export function ScheduleTicketDialog({
  open,
  schedule,
  onClose,
  onSchedule,
  onScheduleChange,
  isLoading = false,
}: ScheduleTicketDialogProps) {
  const now = new Date();

  return (
    <Dialog open={open} onClose={isLoading ? undefined : onClose} fullWidth>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} sx={{ fontSize: "1.2rem", fontWeight: "bold" }}>
            Set schedule
          </Typography>
          <IconButton onClick={onClose} disabled={isLoading}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 3 }}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DateTimePicker
              label="Schedule Date (future date)"
              minDateTime={now}
              value={schedule}
              onChange={(newDate) => onScheduleChange(newDate)}
              sx={{ width: "100%" }}
              disabled={isLoading}
            />
          </LocalizationProvider>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button
          onClick={onSchedule}
          disabled={!schedule || !isBefore(now, schedule) || isLoading}
          variant="contained"
        >
          {isLoading ? "Scheduling..." : "Schedule"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
