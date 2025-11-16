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

import { useViewportOffset } from "../../../hooks/useViewportOffset";
import {
  safetyImpactProps,
  sortedSafetyImpacts,
  maxReasonSafetyImpactLengthInHalf,
} from "../../../utils/const";
import { countFullWidthAndHalfWidthCharacters } from "../../../utils/func";

const TOOLTIP_TEXT_LIMIT = 150;

export function SafetyImpactSelectorView(props) {
  const { fixedTicketSafetyImpact, fixedTicketSafetyImpactChangeReason, onSave, testId } = props;

  const [pendingSafetyImpact, setPendingSafetyImpact] = useState("");
  const [pendingReasonSafetyImpact, setPendingReasonSafetyImpact] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [readMoreDialogOpen, setReadMoreDialogOpen] = useState(false);

  const defaultSafetyImpactItem = "Default";

  const { enqueueSnackbar } = useSnackbar();
  const viewportOffsetTop = useViewportOffset();

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
    onSave(
      pendingSafetyImpact === defaultSafetyImpactItem ? null : pendingSafetyImpact,
      pendingReasonSafetyImpact,
    );
    setOpenDialog(false);
  };

  const handleReasonSafetyImpactLengthCheck = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxReasonSafetyImpactLengthInHalf) {
      enqueueSnackbar(
        `Too long ticket_safety_impact_change_reason. Max length is ${maxReasonSafetyImpactLengthInHalf} in half-width or ${Math.floor(maxReasonSafetyImpactLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
          style: {
            marginTop: `${viewportOffsetTop}px`,
          },
        },
      );
    } else {
      setPendingReasonSafetyImpact(string);
    }
  };

  const isSaveDisabled =
    (fixedTicketSafetyImpact || defaultSafetyImpactItem) === pendingSafetyImpact &&
    (fixedTicketSafetyImpactChangeReason || "") === pendingReasonSafetyImpact;

  const StyledTooltip = styled(({ className, ...props }) => (
    <Tooltip {...props} classes={{ popper: className }} leaveDelay={500} />
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

  const handleOpenReadMoreDialog = () => {
    setReadMoreDialogOpen(true);
  };

  const handleCloseReadMoreDialog = () => {
    setReadMoreDialogOpen(false);
  };

  const reasonText = fixedTicketSafetyImpactChangeReason || "";
  const isLongReason = reasonText.length > TOOLTIP_TEXT_LIMIT;

  const tooltipContent = (
    <>
      <Typography variant="h6" sx={{ px: 1, pt: 1 }}>
        Why was it changed from the default safety impact?
      </Typography>
      <Box sx={{ p: 1 }}>
        <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
          {isLongReason ? `${reasonText.substring(0, TOOLTIP_TEXT_LIMIT)}...` : reasonText}
        </Typography>
      </Box>
      {isLongReason && (
        <Box sx={{ textAlign: "right", px: 1, pb: 1 }}>
          <Button size="small" onClick={handleOpenReadMoreDialog}>
            Read more...
          </Button>
        </Box>
      )}
    </>
  );

  return (
    <Box sx={{ display: "flex", alignItems: "center" }}>
      <FormControl size="small" variant="standard">
        <Select
          data-testid={testId ? `safety-impact-select-${testId}` : "safety-impact-select"}
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
        <StyledTooltip arrow title={tooltipContent}>
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
                data-testid="dialog-safety-impact-select"
                value={pendingSafetyImpact}
                onChange={handleSelectSafetyImpact}
                inputProps={{ "aria-label": "Safety Impact" }}
              >
                <MenuItem key={defaultSafetyImpactItem} value={defaultSafetyImpactItem}>
                  {defaultSafetyImpactItem}
                </MenuItem>
                {sortedSafetyImpacts.map((safetyImpact) => (
                  <MenuItem key={safetyImpact} value={safetyImpact}>
                    {safetyImpactProps[safetyImpact]?.displayName}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <DialogContentText>Provide the reason for this Safety Impact</DialogContentText>
            <TextField
              hiddenLabel
              variant="filled"
              fullWidth
              multiline
              rows={4}
              value={pendingReasonSafetyImpact}
              onChange={(e) => handleReasonSafetyImpactLengthCheck(e.target.value)}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSave} disabled={isSaveDisabled}>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={readMoreDialogOpen} onClose={handleCloseReadMoreDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Why was it changed from the default safety impact?</DialogTitle>
        <DialogContent>
          <DialogContentText
            sx={{
              whiteSpace: "pre-wrap",
              overflowWrap: "break-word",
            }}
          >
            {reasonText}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseReadMoreDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
SafetyImpactSelectorView.propTypes = {
  fixedTicketSafetyImpact: PropTypes.string,
  fixedTicketSafetyImpactChangeReason: PropTypes.string,
  onSave: PropTypes.func.isRequired,
  testId: PropTypes.string,
};
