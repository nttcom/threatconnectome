import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  Box,
  Button,
  Collapse,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  IconButton,
  MenuItem,
  Select,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { tooltipClasses } from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";

import {
  safetyImpactProps,
  sortedSafetyImpacts,
  maxReasonSafetyImpactLengthInHalf,
} from "../../../utils/const";
import { countFullWidthAndHalfWidthCharacters } from "../../../utils/func";

export function SafetyImpactSelectorView(props) {
  const {
    fixedTicketSafetyImpact,
    fixedTicketSafetyImpactChangeReason,
    onRevertedToDefault,
    onSave,
  } = props;

  const [pendingSafetyImpact, setPendingSafetyImpact] = useState("");
  const [pendingReasonSafetyImpact, setPendingReasonSafetyImpact] = useState("");
  const [openDialog, setOpenDialog] = useState(false);

  const defaultSafetyImpactItem = "Default";

  const { enqueueSnackbar } = useSnackbar();

  const handleOpenDialog = () => {
    setPendingSafetyImpact(fixedTicketSafetyImpact || defaultSafetyImpactItem);
    setPendingReasonSafetyImpact(fixedTicketSafetyImpactChangeReason || "");
    setOpenDialog(true);
  };

  const handleSelectSafetyImpact = (e) => {
    setPendingSafetyImpact(e.target.value);
  };

  const handleClose = () => {
    setOpenDialog(false);
  };

  const handleSave = () => {
    if (pendingSafetyImpact === defaultSafetyImpactItem) {
      onRevertedToDefault();
    } else {
      onSave(pendingSafetyImpact, pendingReasonSafetyImpact);
    }
    setOpenDialog(false);
  };

  const handleReasonSafetyImpactLengthCheck = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxReasonSafetyImpactLengthInHalf) {
      enqueueSnackbar(
        `Too long ticket_safety_impact_change_reason. Max length is ${maxReasonSafetyImpactLengthInHalf} in half-width or ${Math.floor(maxReasonSafetyImpactLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
        },
      );
    } else {
      setPendingReasonSafetyImpact(string);
    }
  };

  const isUnchanged =
    (fixedTicketSafetyImpact || defaultSafetyImpactItem) === pendingSafetyImpact &&
    (fixedTicketSafetyImpactChangeReason || "") === pendingReasonSafetyImpact;

  const isReasonRequiredAndEmpty =
    pendingSafetyImpact !== defaultSafetyImpactItem && pendingReasonSafetyImpact === "";

  const isSaveDisabled = isUnchanged || isReasonRequiredAndEmpty;

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
          open={false}
          value={fixedTicketSafetyImpact ? fixedTicketSafetyImpact : defaultSafetyImpactItem}
          onOpen={handleOpenDialog}
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
      {fixedTicketSafetyImpactChangeReason !== null && (
        <StyledTooltip
          arrow
          title={
            <>
              <Typography variant="h6">
                Why was it changed from the default safety impact?
              </Typography>
              <Box sx={{ p: 1 }}>
                <Typography variant="body2">{fixedTicketSafetyImpactChangeReason}</Typography>
              </Box>
            </>
          }
        >
          <IconButton size="small">
            <InfoOutlinedIcon color="primary" fontSize="small" />
          </IconButton>
        </StyledTooltip>
      )}
      <Dialog open={openDialog} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>Safety Impact update</DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            <FormControl fullWidth>
              <Select
                value={pendingSafetyImpact}
                onChange={handleSelectSafetyImpact}
                inputProps={{ "aria-label": "Safety Impact" }}
              >
                <MenuItem value={defaultSafetyImpactItem}>{defaultSafetyImpactItem}</MenuItem>
                {sortedSafetyImpacts.map((safetyImpact) => (
                  <MenuItem key={safetyImpact} value={safetyImpact}>
                    {safetyImpactProps[safetyImpact]?.displayName}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Collapse in={pendingSafetyImpact !== defaultSafetyImpactItem}>
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
            </Collapse>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSave} disabled={isSaveDisabled}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
SafetyImpactSelectorView.propTypes = {
  fixedTicketSafetyImpact: PropTypes.string,
  fixedTicketSafetyImpactChangeReason: PropTypes.string,
  onRevertedToDefault: PropTypes.func.isRequired,
  onSave: PropTypes.func.isRequired,
};
