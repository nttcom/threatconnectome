import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { Box, Drawer, IconButton, Tooltip, Typography } from "@mui/material";
import type { ReactNode } from "react";

type ResponsiveDrawerProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
};

export function ResponsiveDrawer({ open, onClose, title, children }: ResponsiveDrawerProps) {
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box>
        <Tooltip arrow title="Close">
          <IconButton size="large" onClick={onClose} aria-label="close">
            <KeyboardDoubleArrowRightIcon fontSize="inherit" />
          </IconButton>
        </Tooltip>
      </Box>
      <Box sx={{ width: { xs: "100vw", md: 800 }, px: 3, boxSizing: "border-box" }}>
        <Typography variant="h4" sx={{ pb: 1, fontWeight: "bold" }}>
          {title}
        </Typography>
        {children}
      </Box>
    </Drawer>
  );
}
