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

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useGetThreatQuery, useUpdateThreatMutation } from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { safetyImpactProps, sortedSafetyImpacts } from "../../../utils/const";
import { errorToString } from "../../../utils/func";

export function SafetyImpactSelector(props) {
  const { threatId } = props;

  const [pendingSafetyImpact, setPendingSafetyImpact] = useState("");
  const [open, setOpen] = useState(false);
  const [pendingReasonSafetyImpact, setPendingReasonSafetyImpact] = useState("");

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: threat,
    error: threatError,
    isLoading: threatIsLoading,
  } = useGetThreatQuery(threatId, { skip });

  const [updateThreat] = useUpdateThreatMutation();

  const { enqueueSnackbar } = useSnackbar();

  if (skip) return <></>;
  if (threatError) throw new APIError(errorToString(threatError), { api: "getThreat" });
  if (threatIsLoading) return <>Now loading Threat...</>;

  const handleSelectSafetyImpact = (e) => {
    setOpen(true);
    setPendingSafetyImpact(e.target.value);
    setPendingReasonSafetyImpact(threat.reason_safety_impact);
  };

  const handleClose = () => {
    setOpen(false);
    setPendingReasonSafetyImpact("");
  };

  const handleSave = async () => {
    await updateThreat({
      threatId,
      data: {
        threat_safety_impact: pendingSafetyImpact,
        reason_safety_impact: pendingReasonSafetyImpact,
      },
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar("Change safety impact succeeded", { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" }),
      );

    handleClose();
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
          value={threat.threat_safety_impact}
          onChange={(e) => {
            handleSelectSafetyImpact(e);
          }}
        >
          {sortedSafetyImpacts.map((safetyImpact) => (
            <MenuItem key={safetyImpact} value={safetyImpact}>
              {safetyImpactProps[safetyImpact].displayName}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {threat.reason_safety_impact === "" && (
        <StyledTooltip
          arrow
          title={
            <>
              <Typography variant="h6">
                Why was it changed from the default safety impact?
              </Typography>
              <Box sx={{ p: 1 }}>
                <Typography variant="body2">{threat.reason_safety_impact}</Typography>
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
              {threat.threat_safety_impact
                ? safetyImpactProps[threat.threat_safety_impact].displayName
                : "None"}
            </DialogContentText>
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
            value={pendingReasonSafetyImpact}
            onChange={(e) => setPendingReasonSafetyImpact(e.target.value)}
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
SafetyImpactSelector.propTypes = {
  threatId: PropTypes.string.isRequired,
};
