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
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";

import {
  safetyImpactProps,
  sortedSafetyImpacts,
  maxReasonSafetyImpactLengthInHalf,
} from "../../../utils/const";
import { countFullWidthAndHalfWidthCharacters } from "../../../utils/func";

export function SafetyImpactSelectorView(props) {
  const { threatSafetyImpact, reasonSafetyImpact, updateThreatFunction } = props;

  const [pendingSafetyImpact, setPendingSafetyImpact] = useState("");
  const [open, setOpen] = useState(false);
  const [pendingReasonSafetyImpact, setPendingReasonSafetyImpact] = useState("");

  const defaultItem = "Default";

  const { enqueueSnackbar } = useSnackbar();

  const handleSelectSafetyImpact = (e) => {
    if (e.target.value === defaultItem) {
      setPendingSafetyImpact("");
      setPendingReasonSafetyImpact("");
      const requestData = {
        threat_safety_impact: null,
        reason_safety_impact: null,
      };
      updateThreatFunction(requestData);
    } else {
      setPendingSafetyImpact(e.target.value);
      setPendingReasonSafetyImpact(reasonSafetyImpact === null ? "" : reasonSafetyImpact);
      setOpen(true);
    }
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSave = async () => {
    const requestData = {
      threat_safety_impact: pendingSafetyImpact,
      reason_safety_impact: pendingReasonSafetyImpact,
    };
    updateThreatFunction(requestData);
    setOpen(false);
  };

  const handleReasonSafetyImpactLengthCheck = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxReasonSafetyImpactLengthInHalf) {
      enqueueSnackbar(
        `Too long reason_safety_impact. Max length is ${maxReasonSafetyImpactLengthInHalf} in half-width or ${Math.floor(maxReasonSafetyImpactLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
        },
      );
    } else {
      setPendingReasonSafetyImpact(string);
    }
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
          value={threatSafetyImpact ? threatSafetyImpact : defaultItem}
          onChange={(e) => {
            handleSelectSafetyImpact(e);
          }}
        >
          <MenuItem key={defaultItem} value={defaultItem}>
            {defaultItem}
          </MenuItem>
          {sortedSafetyImpacts.map((safetyImpact) => (
            <MenuItem key={safetyImpact} value={safetyImpact}>
              {safetyImpactProps[safetyImpact].displayName}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {reasonSafetyImpact !== null && (
        <StyledTooltip
          arrow
          title={
            <>
              <Typography variant="h6">
                Why was it changed from the default safety impact?
              </Typography>
              <Box sx={{ p: 1 }}>
                <Typography variant="body2">{reasonSafetyImpact}</Typography>
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
            <DialogContentText>
              Current:{" "}
              {threatSafetyImpact ? safetyImpactProps[threatSafetyImpact].displayName : defaultItem}
            </DialogContentText>
            <DialogContentText>
              Updated:{" "}
              {pendingSafetyImpact === ""
                ? defaultItem
                : safetyImpactProps[pendingSafetyImpact].displayName}
            </DialogContentText>
          </Box>
          <DialogContentText>Enter the reason for changing Safety Impact</DialogContentText>
          <TextField
            hiddenLabel
            variant="filled"
            fullWidth
            multiline
            rows={4}
            placeholder="Continue writing here"
            value={pendingReasonSafetyImpact}
            onChange={(e) => handleReasonSafetyImpactLengthCheck(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSave} disabled={pendingReasonSafetyImpact === ""}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
SafetyImpactSelectorView.propTypes = {
  threatSafetyImpact: PropTypes.string.isRequired,
  reasonSafetyImpact: PropTypes.string.isRequired,
  updateThreatFunction: PropTypes.func.isRequired,
};
