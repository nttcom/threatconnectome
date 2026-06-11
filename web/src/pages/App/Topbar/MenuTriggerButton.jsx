import { Button } from "@mui/material";

export function MenuTriggerButton({ active, ariaLabel, children, onClick, sx }) {
  return (
    <Button
      variant="outlined"
      aria-label={ariaLabel}
      aria-haspopup="menu"
      aria-expanded={active}
      onClick={onClick}
      sx={sx}
    >
      {children}
    </Button>
  );
}
