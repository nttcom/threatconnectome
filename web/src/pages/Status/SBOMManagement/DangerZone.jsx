/* eslint-disable react/prop-types, jsx-a11y/no-autofocus */
import CloseIcon from "@mui/icons-material/Close";
import DeleteIcon from "@mui/icons-material/Delete";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import {
  Box,
  Card,
  CardContent,
  Dialog,
  DialogContent,
  IconButton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { isDeleteConfirmationValid } from "../../../utils/SBOMManagement/sbomManagementUtils";

import { AppButton } from "./sharedUiParts";
import { fieldSx, labelSx, sectionIconBoxSx, sectionTitleTextSx, slate } from "./styleTokens";

export function DangerZone({ disabled = false, onDelete, onToggle, open, sbomTitle }) {
  const { t } = useTranslation("status", { keyPrefix: "DangerZone" });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirmationName, setConfirmationName] = useState("");
  const expectedName = sbomTitle || t("untitledSbom");
  const canDelete = isDeleteConfirmationValid(confirmationName, expectedName);

  const closeDialog = () => {
    setDialogOpen(false);
    setConfirmationName("");
  };

  return (
    <Card
      sx={{
        bgcolor: slate[50],
        border: `1px solid ${slate[200]}`,
        borderRadius: 6,
        boxShadow: "none",
        minWidth: 0,
      }}
    >
      <Box
        component="button"
        onClick={() => {
          if (open) {
            closeDialog();
          }
          onToggle();
        }}
        sx={{
          alignItems: "center",
          background: "transparent",
          border: 0,
          cursor: "pointer",
          display: "flex",
          font: "inherit",
          justifyContent: "space-between",
          px: 2,
          py: 1.25,
          textAlign: "left",
          width: "100%",
        }}
        type="button"
      >
        <Stack direction="row" alignItems="center" sx={{ gap: 1, minHeight: 20 }}>
          <Box sx={sectionIconBoxSx}>
            <WarningAmberIcon sx={{ display: "block", fontSize: 18, height: 18, width: 18 }} />
          </Box>
          <Typography sx={sectionTitleTextSx}>{t("dangerZone")}</Typography>
        </Stack>
        <ExpandMoreIcon
          sx={{
            color: slate[400],
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 160ms ease",
          }}
        />
      </Box>

      {open && (
        <CardContent sx={{ pb: 1.5, pt: 0, px: 2 }}>
          <Stack sx={{ gap: 1.5 }}>
            <Typography sx={{ color: slate[500], fontSize: 14, lineHeight: "24px" }}>
              {t("dangerZoneDesc")}
            </Typography>
            <AppButton
              disabled={disabled}
              onClick={() => setDialogOpen(true)}
              startIcon={<DeleteIcon />}
              sx={{ bgcolor: "white", color: slate[700], width: "100%" }}
              variant="outlined"
            >
              {t("openDeleteDialog")}
            </AppButton>
          </Stack>
        </CardContent>
      )}

      <Dialog
        fullWidth
        maxWidth="xs"
        onClose={closeDialog}
        open={dialogOpen}
        PaperProps={{ sx: { borderRadius: 6, p: 1 } }}
      >
        <DialogContent sx={{ p: 2, position: "relative" }}>
          <Box sx={{ pr: 6 }}>
            <Typography sx={{ color: slate[950], fontSize: 18, fontWeight: 800 }}>
              {t("deleteSbomTitle")}
            </Typography>
          </Box>
          <IconButton
            aria-label={t("close")}
            onClick={closeDialog}
            size="small"
            sx={{
              "&:hover": { bgcolor: slate[100], color: slate[900] },
              color: slate[400],
              height: 32,
              p: 0,
              position: "absolute",
              right: 16,
              top: 16,
              width: 32,
            }}
          >
            <CloseIcon sx={{ fontSize: 20 }} />
          </IconButton>
          <Box sx={{ bgcolor: slate[50], borderRadius: 4, mt: 2.5, p: 2 }}>
            <Typography sx={labelSx}>{t("deleteTarget")}</Typography>
            <Typography
              sx={{
                color: slate[800],
                fontSize: 14,
                fontWeight: 700,
                mt: 0.5,
                overflowWrap: "anywhere",
                whiteSpace: "pre-wrap",
              }}
            >
              {expectedName}
            </Typography>
          </Box>
          <Box sx={{ mt: 2.5 }}>
            <Typography component="label" sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
              {t("enterSbomName")}
            </Typography>
            <TextField
              autoFocus
              fullWidth
              onChange={(event) => setConfirmationName(event.target.value)}
              placeholder={expectedName}
              sx={{ ...fieldSx, mt: 1 }}
              value={confirmationName}
            />
            <Typography sx={{ color: slate[400], fontSize: 12, mt: 1 }}>
              {t("enterSbomNameHelp")}
            </Typography>
          </Box>
          <Box
            sx={{
              display: "grid",
              gap: 1,
              gridTemplateColumns: { sm: "1fr 1fr", xs: "1fr" },
              mt: 3,
            }}
          >
            <AppButton onClick={closeDialog} variant="outlined">
              {t("cancel")}
            </AppButton>
            <AppButton
              disabled={!canDelete || disabled}
              onClick={() => {
                if (!canDelete || disabled) {
                  return;
                }
                onDelete();
                closeDialog();
              }}
              startIcon={<DeleteIcon />}
            >
              {t("confirmDelete")}
            </AppButton>
          </Box>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
