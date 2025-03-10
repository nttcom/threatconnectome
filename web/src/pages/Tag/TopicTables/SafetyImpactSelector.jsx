import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  IconButton,
  MenuItem,
  Select,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { tooltipClasses } from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";
import React, { useState } from "react";

export function SafetyImpactSelector() {
  const safetyImpactList = ["Negligible", "Marginal", "Critical", "Catastrophic"];
  const defaultSafetyImpact = safetyImpactList[0];
  const [currentSafetyImpact, setCurrentSafetyImpact] = useState(safetyImpactList[0]);
  const [pendingSafetyImpact, setPendingSafetyImpact] = useState(currentSafetyImpact);
  const [open, setOpen] = useState(false);
  const [reasonChangedSafetyImpact, setReasonChangedSafetyImpact] = useState("");

  const handleClickOpen = (e) => {
    if (e.target.value !== defaultSafetyImpact) {
      setOpen(true);
      setPendingSafetyImpact(e.target.value);
    } else {
      setCurrentSafetyImpact(e.target.value);
    }
  };
  const handleClose = () => {
    setOpen(false);
    setReasonChangedSafetyImpact("");
  };

  const StyledTooltip = styled(({ className, ...props }) => (
    <Tooltip {...props} classes={{ popper: className }} />
  ))(() => ({
    [`& .${tooltipClasses.arrow}`]: {
      "&:before": {
        border: "1px solid #dadde9",
      },
      color: "#f5f5f9",
    },
    [`& .${tooltipClasses.tooltip}`]: {
      backgroundColor: "#f5f5f9",
      color: "rgba(0, 0, 0, 0.87)",
      border: "1px solid #dadde9",
    },
  }));

  return (
    <Box sx={{ display: "flex", alignItems: "center" }}>
      <FormControl sx={{ width: 130 }} size="small" variant="standard">
        <Select
          value={currentSafetyImpact}
          onChange={(e) => {
            handleClickOpen(e);
          }}
        >
          {safetyImpactList.map((safetyImpact) => (
            <MenuItem key={safetyImpact} value={safetyImpact}>
              {safetyImpact}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {currentSafetyImpact !== defaultSafetyImpact && (
        <StyledTooltip
          arrow
          title={
            <>
              <Typography variant="h6">
                Why was it changed from the default safety impact?
              </Typography>
              <Box sx={{ p: 1 }}>
                <Typography variant="body2">
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
                  incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
                  exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute
                  irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
                  pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui
                  officia deserunt mollit anim id est laborum.
                </Typography>
              </Box>
            </>
          }
        >
          <IconButton size="small">
            <InfoOutlinedIcon color="primary" fontSize="small" />
          </IconButton>
        </StyledTooltip>
      )}
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Safety Impact update</DialogTitle>
        <DialogContent>
          <Box sx={{ pb: 2 }}>
            <DialogContentText>Current: {currentSafetyImpact}</DialogContentText>
            <DialogContentText>Updated: {pendingSafetyImpact}</DialogContentText>
          </Box>
          <DialogContentText>Enter the reason for changing Safety Impact</DialogContentText>
          <TextField
            hiddenLabel
            variant="filled"
            fullWidth
            multiline
            rows={4}
            placeholder="Continue writing here"
            value={reasonChangedSafetyImpact}
            onChange={(e) => setReasonChangedSafetyImpact(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            onClick={() => {
              setCurrentSafetyImpact(pendingSafetyImpact);
              handleClose();
            }}
            disabled={!reasonChangedSafetyImpact}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
