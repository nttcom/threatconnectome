import { Menu } from "@mui/material";

import { menuPaperSx } from "./topbarStyles";

export function MenuShell({ anchorEl, ariaLabel, children, open, onClose, width }) {
  return (
    <Menu
      anchorEl={anchorEl}
      open={open}
      onClose={onClose}
      slotProps={{
        list: { "aria-label": ariaLabel, sx: { p: 0.75 } },
        paper: { sx: { ...menuPaperSx, width, maxWidth: width } },
      }}
    >
      {children}
    </Menu>
  );
}
