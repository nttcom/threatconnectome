import LogoutIcon from "@mui/icons-material/Logout";
import SettingsIcon from "@mui/icons-material/Settings";
import {
  Divider,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  useMediaQuery,
  useTheme,
} from "@mui/material";

import { compactMenuItemSx, menuPaperSx, menuWidths } from "./topbarStyles";

export function UserMenu({ anchorEl, labels, open, onClose, onLogout, onOpenAccountSettings }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const mobileSlotProps = isMobile
    ? {
        list: { sx: { p: 0.75 } },
        paper: {
          sx: {
            ...menuPaperSx,
            width: menuWidths.default.xs,
            maxWidth: "calc(100vw - 16px)",
          },
        },
      }
    : undefined;

  const handleAccountSettings = () => {
    onOpenAccountSettings();
    onClose();
  };

  const handleLogout = () => {
    onLogout();
    onClose();
  };

  return (
    <Menu
      anchorEl={anchorEl}
      open={open}
      onClose={onClose}
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "right",
      }}
      transformOrigin={{
        vertical: "top",
        horizontal: "right",
      }}
      slotProps={mobileSlotProps}
    >
      <MenuItem onClick={handleAccountSettings} sx={isMobile ? compactMenuItemSx : undefined}>
        <ListItemIcon>
          <SettingsIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>{labels.settings}</ListItemText>
      </MenuItem>
      <Divider sx={isMobile ? { my: 0.75 } : undefined} />
      <MenuItem onClick={handleLogout} sx={isMobile ? compactMenuItemSx : undefined}>
        <ListItemIcon>
          <LogoutIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>{labels.logout}</ListItemText>
      </MenuItem>
    </Menu>
  );
}
