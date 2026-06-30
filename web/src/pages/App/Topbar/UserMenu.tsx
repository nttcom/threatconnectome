import LogoutIcon from "@mui/icons-material/Logout";
import SettingsIcon from "@mui/icons-material/Settings";
import {
  Box,
  Divider,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";

import { colors, compactMenuItemSx, ellipsisTextSx, menuPaperSx, menuWidths } from "./topbarStyles";
import type { MenuAnchor, TopbarLabels } from "./topbarTypes";

export function UserMenu({
  accountSettingsEnabled,
  anchorEl,
  labels,
  open,
  onClose,
  onLogout,
  onOpenAccountSettings,
  userEmail,
}: {
  accountSettingsEnabled: boolean;
  anchorEl: MenuAnchor;
  labels: TopbarLabels;
  open: boolean;
  onClose: () => void;
  onLogout: () => void | Promise<void>;
  onOpenAccountSettings: () => void;
  userEmail?: string | null;
}) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const displayEmail = userEmail?.trim() || null;
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
    if (accountSettingsEnabled) {
      onOpenAccountSettings();
    }
    onClose();
  };

  const handleLogout = () => {
    void onLogout();
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
      {displayEmail ? (
        <>
          <Box
            role="presentation"
            sx={{
              px: isMobile ? 1.5 : 2,
              py: isMobile ? 1.25 : 1.5,
              maxWidth: isMobile ? menuWidths.default.xs : menuWidths.default.sm,
            }}
          >
            <Typography
              title={displayEmail}
              sx={{
                ...ellipsisTextSx,
                color: colors.ink700,
                fontSize: 14,
                fontWeight: 600,
                lineHeight: 1.35,
              }}
            >
              {displayEmail}
            </Typography>
          </Box>
          <Divider sx={isMobile ? { my: 0.75 } : undefined} />
        </>
      ) : null}
      <MenuItem
        disabled={!accountSettingsEnabled}
        onClick={handleAccountSettings}
        sx={isMobile ? compactMenuItemSx : undefined}
      >
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
