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
import PropTypes from "prop-types";
import React, { useState } from "react";

import { safetyImpactProps, sortedSafetyImpacts } from "../../../utils/const";

export function SafetyImpactSelectorView(props) {
  const {
    defaultSafetyImpactItem,
    fixedThreatSafetyImpact,
    fixedReasonSafetyImpact,
    pendingSafetyImpact,
    pendingReasonSafetyImpact,
    onSelectSafetyImpact,
    onChangeReason,
    onSaveReason,
  } = props;

  const [openReasonDialog, setOpenReasonDialog] = useState(false);

  const handleSelectSafetyImpact = (e) => {
    onSelectSafetyImpact(e.target.value);

    if (e.target.value !== defaultSafetyImpactItem) {
      setOpenReasonDialog(true);
    }
  };

  const handleClose = () => {
    setOpenReasonDialog(false);
  };

  const handleSaveReason = async () => {
    onSaveReason();
    setOpenReasonDialog(false);
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
          value={fixedThreatSafetyImpact ? fixedThreatSafetyImpact : defaultSafetyImpactItem}
          onChange={(e) => {
            handleSelectSafetyImpact(e);
          }}
        >
          <MenuItem key={defaultSafetyImpactItem} value={defaultSafetyImpactItem}>
            {defaultSafetyImpactItem}
          </MenuItem>
          {sortedSafetyImpacts.map((safetyImpact) => (
            <MenuItem key={safetyImpact} value={safetyImpact}>
              {safetyImpactProps[safetyImpact].displayName}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {fixedReasonSafetyImpact !== null && (
        <StyledTooltip
          arrow
          title={
            <>
              <Typography variant="h6">
                Why was it changed from the default safety impact?
              </Typography>
              <Box sx={{ p: 1 }}>
                <Typography variant="body2">{fixedReasonSafetyImpact}</Typography>
              </Box>
            </>
          }
        >
          <IconButton size="small">
            <InfoOutlinedIcon color="primary" fontSize="small" />
          </IconButton>
        </StyledTooltip>
      )}
      <Dialog open={openReasonDialog} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Safety Impact update</DialogTitle>
        <DialogContent>
          <Box sx={{ pb: 2 }}>
            <DialogContentText>
              Current:{" "}
              {fixedThreatSafetyImpact
                ? safetyImpactProps[fixedThreatSafetyImpact].displayName
                : defaultSafetyImpactItem}
            </DialogContentText>
            <DialogContentText>
              Updated:{" "}
              {pendingSafetyImpact === ""
                ? defaultSafetyImpactItem
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
            onChange={(e) => onChangeReason(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSaveReason} disabled={pendingReasonSafetyImpact === ""}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
SafetyImpactSelectorView.propTypes = {
  defaultSafetyImpactItem: PropTypes.string.isRequired,
  fixedThreatSafetyImpact: PropTypes.string.isRequired,
  fixedReasonSafetyImpact: PropTypes.string.isRequired,
  pendingSafetyImpact: PropTypes.string.isRequired,
  pendingReasonSafetyImpact: PropTypes.string.isRequired,
  onSelectSafetyImpact: PropTypes.func.isRequired,
  onChangeReason: PropTypes.func.isRequired,
  onSaveReason: PropTypes.func.isRequired,
};
