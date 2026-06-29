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
import type { SelectChangeEvent } from "@mui/material";
import { tooltipClasses } from "@mui/material/Tooltip";
import type { TooltipProps } from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import type { SafetyImpactEnum } from "../../../types/types.gen";
import { useViewportOffset } from "../../hooks/useViewportOffset";
import {
  safetyImpactProps,
  sortedSafetyImpacts,
  maxReasonSafetyImpactLengthInHalf,
} from "../../utils/const";
import { countFullWidthAndHalfWidthCharacters } from "../../utils/func";

const TOOLTIP_TEXT_LIMIT = 150;
const DEFAULT_SAFETY_IMPACT_ITEM = "Default";

type SafetyImpactSelectorViewProps = {
  fixedTicketSafetyImpact: SafetyImpactEnum | null;
  fixedTicketSafetyImpactChangeReason: string | null;
  onSave: (safetyImpact: SafetyImpactEnum | null, reason: string) => void;
};

const StyledTooltip = styled(({ className, ...props }: TooltipProps) => (
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

export function SafetyImpactSelectorView(props: SafetyImpactSelectorViewProps) {
  const { fixedTicketSafetyImpact, fixedTicketSafetyImpactChangeReason, onSave } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "SafetyImpactSelectorView" });

  const [pendingSafetyImpact, setPendingSafetyImpact] = useState<
    SafetyImpactEnum | typeof DEFAULT_SAFETY_IMPACT_ITEM
  >(DEFAULT_SAFETY_IMPACT_ITEM);
  const [pendingReasonSafetyImpact, setPendingReasonSafetyImpact] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [readMoreDialogOpen, setReadMoreDialogOpen] = useState(false);

  const { enqueueSnackbar } = useSnackbar();
  const viewportOffsetTop = useViewportOffset();

  const handleOpenDialog = () => {
    setPendingSafetyImpact(fixedTicketSafetyImpact || DEFAULT_SAFETY_IMPACT_ITEM);
    setPendingReasonSafetyImpact(fixedTicketSafetyImpactChangeReason || "");
    setOpenDialog(true);
  };

  const handleSelectSafetyImpact = (e: SelectChangeEvent) => {
    setPendingSafetyImpact(e.target.value as SafetyImpactEnum | typeof DEFAULT_SAFETY_IMPACT_ITEM);
  };

  const handleClose = () => {
    setOpenDialog(false);
  };

  const handleSave = () => {
    onSave(
      pendingSafetyImpact === DEFAULT_SAFETY_IMPACT_ITEM ? null : pendingSafetyImpact,
      pendingReasonSafetyImpact,
    );
    setOpenDialog(false);
  };

  const handleReasonSafetyImpactLengthCheck = (string: string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxReasonSafetyImpactLengthInHalf) {
      enqueueSnackbar(
        t("reasonTooLong", {
          maxHalf: maxReasonSafetyImpactLengthInHalf,
          maxFull: Math.floor(maxReasonSafetyImpactLengthInHalf / 2),
        }),
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
    (fixedTicketSafetyImpact || DEFAULT_SAFETY_IMPACT_ITEM) === pendingSafetyImpact &&
    (fixedTicketSafetyImpactChangeReason || "") === pendingReasonSafetyImpact;

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
        {t("tooltipTitle")}
      </Typography>
      <Box sx={{ p: 1 }}>
        <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
          {isLongReason ? `${reasonText.substring(0, TOOLTIP_TEXT_LIMIT)}...` : reasonText}
        </Typography>
      </Box>
      {isLongReason && (
        <Box sx={{ textAlign: "right", px: 1, pb: 1 }}>
          <Button size="small" onClick={handleOpenReadMoreDialog}>
            {t("readMore")}
          </Button>
        </Box>
      )}
    </>
  );

  return (
    <Box sx={{ display: "flex", alignItems: "center" }}>
      <FormControl size="small" variant="standard">
        <Select
          open={false}
          value={fixedTicketSafetyImpact ? fixedTicketSafetyImpact : DEFAULT_SAFETY_IMPACT_ITEM}
          onOpen={handleOpenDialog}
        >
          <MenuItem key={DEFAULT_SAFETY_IMPACT_ITEM} value={DEFAULT_SAFETY_IMPACT_ITEM}>
            {DEFAULT_SAFETY_IMPACT_ITEM}
          </MenuItem>
          {(sortedSafetyImpacts as SafetyImpactEnum[]).map((safetyImpact) => (
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
        <DialogTitle>{t("dialogTitle")}</DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            <FormControl fullWidth>
              <Select
                value={pendingSafetyImpact}
                onChange={handleSelectSafetyImpact}
                inputProps={{ "aria-label": "Safety Impact" }}
              >
                <MenuItem key={DEFAULT_SAFETY_IMPACT_ITEM} value={DEFAULT_SAFETY_IMPACT_ITEM}>
                  {DEFAULT_SAFETY_IMPACT_ITEM}
                </MenuItem>
                {(sortedSafetyImpacts as SafetyImpactEnum[]).map((safetyImpact) => (
                  <MenuItem key={safetyImpact} value={safetyImpact}>
                    {safetyImpactProps[safetyImpact]?.displayName}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <DialogContentText>{t("reasonPrompt")}</DialogContentText>
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
          <Button onClick={handleClose}>{t("cancel")}</Button>
          <Button onClick={handleSave} disabled={isSaveDisabled}>
            {t("save")}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={readMoreDialogOpen} onClose={handleCloseReadMoreDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{t("readMoreDialogTitle")}</DialogTitle>
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
          <Button onClick={handleCloseReadMoreDialog}>{t("close")}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
