import { Button } from "@mui/material";
import type { ReactNode } from "react";

import type { MenuToggleHandler, Sx } from "./topbarTypes";

type MenuTriggerButtonProps = {
  active: boolean;
  ariaLabel: string;
  children: ReactNode;
  disabled?: boolean;
  onClick: MenuToggleHandler;
  sx?: Sx;
};

export function MenuTriggerButton({
  active,
  ariaLabel,
  children,
  disabled,
  onClick,
  sx,
}: MenuTriggerButtonProps) {
  return (
    <Button
      variant="outlined"
      aria-label={ariaLabel}
      aria-haspopup="menu"
      aria-expanded={active}
      disabled={disabled}
      onClick={onClick}
      sx={sx}
    >
      {children}
    </Button>
  );
}
