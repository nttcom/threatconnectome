import {
  Box,
  CircularProgress,
  Dialog,
  DialogContent,
  DialogTitle,
  Typography,
} from "@mui/material";
import { useTranslation } from "react-i18next";

type Props = {
  isOpen: boolean;
  text: string;
};

export function WaitingModal({ isOpen, text }: Props) {
  const { t } = useTranslation("status", { keyPrefix: "WaitingModal" });

  return (
    <Dialog fullWidth open={isOpen}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row" sx={{ mt: 3 }}>
          <Typography flexGrow={1} variant="inherit" sx={{ ml: 2 }}>
            {t("inProgress", { text })}
          </Typography>
          <CircularProgress sx={{ mr: 4 }} />
        </Box>
      </DialogTitle>
      <DialogContent></DialogContent>
    </Dialog>
  );
}
