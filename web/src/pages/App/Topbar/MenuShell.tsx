import { Menu } from "@mui/material";
import type { ReactNode } from "react";

import { menuPaperSx } from "./topbarStyles";
import type { MenuAnchor, MenuWidth } from "./topbarTypes";

type MenuShellProps = {
  anchorEl: MenuAnchor;
  ariaLabel: string;
  children: ReactNode;
  open: boolean;
  onClose: () => void;
  width: MenuWidth;
};

export function MenuShell({ anchorEl, ariaLabel, children, open, onClose, width }: MenuShellProps) {
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
