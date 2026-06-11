import "@fontsource/inter/700.css";

/* eslint-disable react/prop-types */

import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import AddIcon from "@mui/icons-material/Add";
import CheckIcon from "@mui/icons-material/Check";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import GroupIcon from "@mui/icons-material/Group";
import LogoutIcon from "@mui/icons-material/Logout";
import SettingsIcon from "@mui/icons-material/Settings";
import {
  AppBar,
  Box,
  Button,
  Chip,
  Divider,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Stack,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

const colors = {
  ink900: "#111827",
  ink700: "#374151",
  ink500: "#6B7280",
  ink400: "#9CA3AF",
  slate50: "#F8FAFC",
  slate100: "#F1F5F9",
  slate200: "#E2E8F0",
  slate300: "#CBD5E1",
  brand50: "#ECFDF5",
  brand100: "#D1FAE5",
  brand700: "#047857",
  red50: "#FEF2F2",
  red100: "#FEE2E2",
  red600: "#DC2626",
  amber50: "#FFFBEB",
  amber100: "#FEF3C7",
  amber700: "#B45309",
  sky50: "#F0F9FF",
  sky100: "#E0F2FE",
  sky700: "#0369A1",
  violet50: "#F5F3FF",
  violet100: "#EDE9FE",
  violet700: "#6D28D9",
};

const tonePalette = {
  brand: { bg: colors.brand50, color: colors.brand700, ring: colors.brand100 },
  sky: { bg: colors.sky50, color: colors.sky700, ring: colors.sky100 },
  red: { bg: colors.red50, color: colors.red600, ring: colors.red100 },
  amber: { bg: colors.amber50, color: colors.amber700, ring: colors.amber100 },
  violet: { bg: colors.violet50, color: colors.violet700, ring: colors.violet100 },
  slate: { bg: "#fff", color: colors.ink500, ring: colors.slate200 },
};

const menuWidths = {
  page: { xs: "calc(100vw - 16px)", sm: 336 },
  default: { xs: "calc(100vw - 16px)", sm: 288 },
};

const menuPaperSx = {
  mt: 1,
  border: `1px solid ${colors.slate200}`,
  borderRadius: 3,
  boxShadow: "0 18px 44px rgba(17, 24, 39, 0.14), 0 2px 8px rgba(17, 24, 39, 0.08)",
  overflow: "hidden",
};

const controlButtonSx = {
  height: 40,
  minHeight: 40,
  borderColor: `${colors.slate300} !important`,
  color: colors.ink700,
  bgcolor: "#fff",
  borderRadius: "8px",
  boxShadow: "0 1px 2px rgba(17, 24, 39, 0.05)",
  textTransform: "none",
  fontWeight: 600,
  lineHeight: 1,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  "& .MuiButton-endIcon": {
    ml: 0.75,
    mr: 0,
    color: colors.ink400,
  },
  "&:hover": {
    borderColor: `${colors.slate300} !important`,
    bgcolor: colors.slate50,
  },
  "&:focus-visible": {
    outline: `2px solid ${colors.brand100}`,
    outlineOffset: 2,
  },
};

const compactTopbarButtonSx = {
  ...controlButtonSx,
  width: 40,
  height: 40,
  minWidth: 40,
  px: 0,
};

const responsiveTopbarButtonSx = {
  ...controlButtonSx,
  minWidth: { xs: 40, sm: 0 },
  width: { xs: 40, sm: "auto" },
  px: { xs: 0, sm: 1.5 },
};

const topbarButtonContentSx = {
  alignItems: "center",
  gap: 1,
  minWidth: 0,
  maxWidth: "100%",
  overflow: "hidden",
};

const ellipsisTextSx = {
  textOverflow: "ellipsis",
  overflow: "hidden",
  whiteSpace: "nowrap",
};

const compactMenuItemSx = {
  mx: 0.75,
  my: 0.25,
  px: 1.5,
  py: 1.25,
  borderRadius: 2,
};

const currentChipSx = {
  height: 20,
  fontSize: 11,
  fontWeight: 600,
};

const teamMenuListSx = {
  maxHeight: 252,
  overflowY: "auto",
  overscrollBehavior: "contain",
  py: 0.25,
  scrollbarWidth: "thin",
  scrollbarColor: `${colors.ink400} transparent`,
  "&::-webkit-scrollbar": {
    width: 8,
  },
  "&::-webkit-scrollbar-thumb": {
    borderRadius: 999,
    bgcolor: colors.ink400,
    border: "2px solid transparent",
    backgroundClip: "content-box",
  },
  "&::-webkit-scrollbar-track": {
    bgcolor: "transparent",
  },
};

function useMenu() {
  const [activeMenu, setActiveMenu] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);

  const close = () => {
    setActiveMenu(null);
    setAnchorEl(null);
  };

  const toggle = (menuName) => (event) => {
    if (activeMenu === menuName) {
      close();
    } else {
      setActiveMenu(menuName);
      setAnchorEl(event.currentTarget);
    }
  };

  const isOpen = (menuName) => activeMenu === menuName;

  return { anchorEl, close, toggle, isOpen };
}

function IconRenderer({ icon: Icon, size = 18 }) {
  return <Icon aria-hidden="true" sx={{ fontSize: size }} />;
}

function IconBadge({ icon, size = 32, iconSize = 18, radius = 8, tone = "slate" }) {
  const palette = tonePalette[tone];

  return (
    <Box
      sx={{
        display: "grid",
        placeItems: "center",
        width: size,
        height: size,
        flexShrink: 0,
        borderRadius: `${radius}px`,
        bgcolor: palette.bg,
        color: palette.color,
        border: `1px solid ${palette.ring}`,
      }}
    >
      <IconRenderer icon={icon} size={iconSize} />
    </Box>
  );
}

function MenuTriggerButton({ active, ariaLabel, children, onClick, sx }) {
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

function CurrentChip({ label, sx }) {
  return (
    <Chip
      label={label}
      size="small"
      sx={{
        ...currentChipSx,
        bgcolor: colors.brand50,
        color: colors.brand700,
        border: `1px solid ${colors.brand100}`,
        ...sx,
      }}
    />
  );
}

function MarkLogo({ size = 32, framed = true }) {
  const markGeometry = framed
    ? {
        path: "M168 164 L344 164 L268 346",
        strokeWidth: 54,
        topLeft: { cx: 168, cy: 164, r: 60 },
        topRight: { cx: 344, cy: 164, r: 60 },
        bottom: { cx: 268, cy: 346, r: 70 },
        highlightRadius: 26,
      }
    : {
        path: "M156 152 L356 152 L268 358",
        strokeWidth: 58,
        topLeft: { cx: 156, cy: 152, r: 66 },
        topRight: { cx: 356, cy: 152, r: 66 },
        bottom: { cx: 268, cy: 358, r: 76 },
        highlightRadius: 28,
      };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      fill="none"
      role="img"
      aria-label="Threatconnectome"
    >
      {framed ? (
        <>
          <rect width="512" height="512" rx="112" fill="#FFFFFF" />
          <rect
            x="22"
            y="22"
            width="468"
            height="468"
            rx="90"
            stroke={colors.slate300}
            strokeWidth="16"
          />
        </>
      ) : null}
      <path
        d={markGeometry.path}
        stroke="#0B1220"
        strokeWidth={markGeometry.strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle
        cx={markGeometry.topLeft.cx}
        cy={markGeometry.topLeft.cy}
        r={markGeometry.topLeft.r}
        fill="#0B1220"
      />
      <circle
        cx={markGeometry.topRight.cx}
        cy={markGeometry.topRight.cy}
        r={markGeometry.topRight.r}
        fill="#0B1220"
      />
      <circle
        cx={markGeometry.bottom.cx}
        cy={markGeometry.bottom.cy}
        r={markGeometry.bottom.r}
        fill="#22C55E"
      />
      <circle
        cx={markGeometry.bottom.cx}
        cy={markGeometry.bottom.cy}
        r={markGeometry.highlightRadius}
        fill="#FFFFFF"
        opacity="0.22"
      />
    </svg>
  );
}

function WordmarkLogo() {
  return (
    <Stack direction="row" sx={{ alignItems: "center", gap: 1 }}>
      <MarkLogo />
      <Typography
        sx={{
          fontFamily: '"Inter", sans-serif',
          fontSize: 16,
          fontWeight: 700,
          color: colors.ink900,
          letterSpacing: 0,
          lineHeight: 1,
          userSelect: "none",
        }}
      >
        Threatconnectome
      </Typography>
    </Stack>
  );
}

function TopbarLogoLink({ ariaLabel, onClick }) {
  return (
    <Box
      component="a"
      href="/"
      aria-label={ariaLabel}
      onClick={onClick}
      sx={{
        display: "flex",
        alignItems: "center",
        height: 40,
        flexShrink: 0,
        textDecoration: "none",
      }}
    >
      <Box sx={{ display: { xs: "block", sm: "none" }, lineHeight: 0 }}>
        <MarkLogo size={38} framed={false} />
      </Box>
      <Box sx={{ display: { xs: "none", sm: "block" } }}>
        <WordmarkLogo />
      </Box>
    </Box>
  );
}

function MenuShell({ anchorEl, ariaLabel, children, open, onClose, width }) {
  return (
    <Menu
      anchorEl={anchorEl}
      open={open}
      onClose={onClose}
      slotProps={{
        list: { "aria-label": ariaLabel, sx: { p: 0.75 } },
        paper: { sx: { ...menuPaperSx, width, maxWidth: width.sm } },
      }}
    >
      {children}
    </Menu>
  );
}

function MenuHeader({ title, detail }) {
  return (
    <Box sx={{ px: 2, py: 1.5, borderBottom: `1px solid ${colors.slate100}` }}>
      <Typography
        sx={{
          color: colors.ink500,
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: 0.7,
          textTransform: "uppercase",
        }}
      >
        {title}
      </Typography>
      {detail ? (
        <Typography sx={{ mt: 0.25, color: colors.ink400, fontSize: 12 }}>{detail}</Typography>
      ) : null}
    </Box>
  );
}

function PageMenuItem({ current, item, labels, onSelect }) {
  return (
    <MenuItem
      selected={current}
      onClick={() => onSelect(item)}
      sx={{
        ...compactMenuItemSx,
        alignItems: "center",
        gap: 1.5,
        whiteSpace: "normal",
        bgcolor: current ? colors.brand50 : "transparent",
        outline: current ? `1px solid ${colors.brand100}` : "none",
        "&.Mui-selected": {
          bgcolor: colors.brand50,
        },
        "&.Mui-selected:hover": {
          bgcolor: colors.brand50,
        },
        "&:hover": { bgcolor: current ? colors.brand50 : colors.slate50 },
      }}
    >
      <IconBadge icon={item.icon} tone={item.tone} />
      <Box sx={{ minWidth: 0 }}>
        <Stack direction="row" sx={{ alignItems: "center", gap: 1, flexWrap: "wrap" }}>
          <Typography sx={{ color: colors.ink900, fontSize: 14, fontWeight: 600 }}>
            {item.label}
          </Typography>
          {current ? <CurrentChip label={labels.current} sx={{ bgcolor: "#fff" }} /> : null}
        </Stack>
      </Box>
    </MenuItem>
  );
}

function PageMenu({ anchorEl, currentPage, labels, open, onClose, onSelectPage, pageItems }) {
  const selectPage = (item) => {
    onSelectPage(item);
    onClose();
  };

  return (
    <MenuShell
      anchorEl={anchorEl}
      ariaLabel={labels.pageSwitch}
      open={open}
      onClose={onClose}
      width={menuWidths.page}
    >
      <MenuHeader title={labels.pageSwitch} />
      {pageItems.map((item) => (
        <PageMenuItem
          key={item.id}
          current={item.id === currentPage.id}
          item={item}
          labels={labels}
          onSelect={selectPage}
        />
      ))}
    </MenuShell>
  );
}

function TeamMenuItem({ item, onSelectTeam }) {
  return (
    <MenuItem
      onClick={() => onSelectTeam(item.id)}
      sx={{
        ...compactMenuItemSx,
        justifyContent: "space-between",
        gap: 2,
        bgcolor: item.current ? colors.slate50 : "transparent",
        "&:hover": { bgcolor: colors.slate50 },
      }}
    >
      <Box sx={{ minWidth: 0 }}>
        <Typography sx={{ color: colors.ink900, fontSize: 14, fontWeight: 600 }}>
          {item.name}
        </Typography>
        {item.detail ? (
          <Typography sx={{ color: colors.ink500, fontSize: 12, lineHeight: 1.7 }}>
            {item.detail}
          </Typography>
        ) : null}
      </Box>
      {item.current ? <IconRenderer icon={CheckIcon} size={18} /> : null}
    </MenuItem>
  );
}

function TeamMenuList({ labels, onCreateTeam, onSelectTeam, teamItems }) {
  const selectTeam = (teamId) => {
    onSelectTeam(teamId);
  };

  return (
    <>
      <Box sx={teamMenuListSx}>
        {teamItems.map((item) => (
          <TeamMenuItem key={item.id} item={item} onSelectTeam={selectTeam} />
        ))}
      </Box>
      <Divider sx={{ my: 0.75 }} />
      <MenuItem onClick={onCreateTeam} sx={compactMenuItemSx}>
        <ListItemIcon>
          <AddIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>{labels.createTeam}</ListItemText>
      </MenuItem>
    </>
  );
}

function TeamMenu({ anchorEl, labels, open, onClose, onCreateTeam, onSelectTeam, teamItems }) {
  const closeAfterCreateTeam = () => {
    onCreateTeam();
    onClose();
  };

  const closeAfterSelectTeam = (teamId) => {
    onSelectTeam(teamId);
    onClose();
  };

  return (
    <MenuShell
      anchorEl={anchorEl}
      ariaLabel={labels.teamSelect}
      open={open}
      onClose={onClose}
      width={menuWidths.default}
    >
      <MenuHeader title={labels.teamSelect} />
      <TeamMenuList
        labels={labels}
        onCreateTeam={closeAfterCreateTeam}
        onSelectTeam={closeAfterSelectTeam}
        teamItems={teamItems}
      />
    </MenuShell>
  );
}

function UserMenu({ anchorEl, labels, open, onClose, onLogout, onOpenAccountSettings }) {
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

function PageMenuButton({ active, currentPage, labels, onClick }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const compactLabel = currentPage.shortLabel ?? currentPage.label;

  if (isMobile) {
    return (
      <MenuTriggerButton
        active={active}
        ariaLabel={labels.pageMenu}
        onClick={onClick}
        sx={compactTopbarButtonSx}
      >
        <IconBadge
          icon={currentPage.icon}
          size={28}
          iconSize={18}
          radius={8}
          tone={currentPage.tone}
        />
      </MenuTriggerButton>
    );
  }

  return (
    <MenuTriggerButton
      active={active}
      ariaLabel={labels.pageMenu}
      onClick={onClick}
      sx={{
        ...responsiveTopbarButtonSx,
        maxWidth: { sm: 168, md: 220 },
        minWidth: 0,
        gap: 0.5,
      }}
    >
      <Stack direction="row" sx={topbarButtonContentSx}>
        <IconBadge
          icon={currentPage.icon}
          size={24}
          iconSize={15}
          radius={6}
          tone={currentPage.tone}
        />
        <Typography
          noWrap
          sx={{
            display: { xs: "none", sm: "block", md: "none" },
            minWidth: 0,
            fontSize: 14,
            fontWeight: 600,
            ...ellipsisTextSx,
          }}
        >
          {compactLabel}
        </Typography>
        <Typography
          noWrap
          sx={{
            display: { xs: "none", md: "block" },
            minWidth: 0,
            fontSize: 14,
            fontWeight: 600,
            ...ellipsisTextSx,
          }}
        >
          {currentPage.label}
        </Typography>
        <Box sx={{ color: colors.ink400, flexShrink: 0 }}>
          <IconRenderer icon={ExpandMoreIcon} size={16} />
        </Box>
      </Stack>
    </MenuTriggerButton>
  );
}

function TeamMenuButton({ active, currentTeam, labels, onClick }) {
  return (
    <MenuTriggerButton
      active={active}
      ariaLabel={labels.teamMenu}
      onClick={onClick}
      sx={responsiveTopbarButtonSx}
    >
      <Stack direction="row" sx={topbarButtonContentSx}>
        <IconBadge icon={GroupIcon} size={24} iconSize={15} radius={6} />
        <Typography
          noWrap
          sx={{
            display: { xs: "none", sm: "block" },
            maxWidth: 144,
            fontSize: 14,
            fontWeight: 600,
          }}
        >
          {currentTeam?.name ?? labels.noTeam}
        </Typography>
        <Box sx={{ display: { xs: "none", sm: "flex" }, color: colors.ink400 }}>
          <IconRenderer icon={ExpandMoreIcon} size={16} />
        </Box>
      </Stack>
    </MenuTriggerButton>
  );
}

function UserMenuButton({ active, labels, onClick }) {
  const userIcon = <IconRenderer icon={AccountCircleIcon} size={22} />;

  return (
    <MenuTriggerButton
      active={active}
      ariaLabel={labels.userMenu}
      onClick={onClick}
      sx={compactTopbarButtonSx}
    >
      {userIcon}
    </MenuTriggerButton>
  );
}

export function TopbarView({
  currentPage,
  currentTeam,
  labels,
  languageSwitcher,
  onCreateTeam,
  onLogout,
  onOpenAccountSettings,
  onSelectHome,
  onSelectPage,
  onSelectTeam,
  pageItems,
  teamItems,
}) {
  const { anchorEl, close, toggle, isOpen } = useMenu();

  return (
    <>
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          height: 64,
          bgcolor: "#fff",
          color: colors.ink900,
          borderBottom: `1px solid ${colors.slate200}`,
        }}
      >
        <Toolbar
          sx={{
            minHeight: "64px !important",
            height: 64,
            px: { xs: 2, sm: 3, lg: 4 },
            py: 0,
            gap: { sm: 3 },
            alignItems: "center",
            display: { xs: "grid", sm: "flex" },
            gridTemplateColumns: { xs: "40px 40px 1fr 40px 40px", sm: "none" },
          }}
        >
          <Stack
            direction="row"
            sx={{
              display: { xs: "none", sm: "flex" },
              alignItems: "center",
              gap: 3,
              minWidth: 0,
              flex: "1 1 auto",
              height: "100%",
            }}
          >
            <TopbarLogoLink ariaLabel={labels.homeAriaLabel} onClick={onSelectHome} />
            <Box
              sx={{
                display: { xs: "none", sm: "block" },
                width: "1px",
                height: 32,
                flexShrink: 0,
                bgcolor: colors.slate200,
              }}
            />
            <PageMenuButton
              active={isOpen("page")}
              currentPage={currentPage}
              labels={labels}
              onClick={toggle("page")}
            />
          </Stack>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "start" }}>
            <PageMenuButton
              active={isOpen("page")}
              currentPage={currentPage}
              labels={labels}
              onClick={toggle("page")}
            />
          </Box>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "start" }}>
            <TeamMenuButton
              active={isOpen("team")}
              currentTeam={currentTeam}
              labels={labels}
              onClick={toggle("team")}
            />
          </Box>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "center" }}>
            <TopbarLogoLink ariaLabel={labels.homeAriaLabel} onClick={onSelectHome} />
          </Box>

          <Stack
            direction="row"
            sx={{
              display: { xs: "none", sm: "flex" },
              alignItems: "center",
              gap: 1.5,
              flexShrink: 0,
              height: "100%",
            }}
          >
            <TeamMenuButton
              active={isOpen("team")}
              currentTeam={currentTeam}
              labels={labels}
              onClick={toggle("team")}
            />
            {languageSwitcher}
            <UserMenuButton active={isOpen("user")} labels={labels} onClick={toggle("user")} />
          </Stack>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "end" }}>
            {languageSwitcher}
          </Box>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "end" }}>
            <UserMenuButton active={isOpen("user")} labels={labels} onClick={toggle("user")} />
          </Box>
        </Toolbar>
      </AppBar>

      <PageMenu
        anchorEl={anchorEl}
        currentPage={currentPage}
        labels={labels}
        open={isOpen("page")}
        onClose={close}
        onSelectPage={onSelectPage}
        pageItems={pageItems}
      />
      <TeamMenu
        anchorEl={anchorEl}
        labels={labels}
        open={isOpen("team")}
        onClose={close}
        onCreateTeam={onCreateTeam}
        onSelectTeam={onSelectTeam}
        teamItems={teamItems}
      />
      <UserMenu
        anchorEl={anchorEl}
        labels={labels}
        open={isOpen("user")}
        onClose={close}
        onLogout={onLogout}
        onOpenAccountSettings={onOpenAccountSettings}
      />
    </>
  );
}

const pageItemType = PropTypes.shape({
  icon: PropTypes.elementType.isRequired,
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  shortLabel: PropTypes.string,
  tone: PropTypes.string.isRequired,
});

const teamItemType = PropTypes.shape({
  current: PropTypes.bool,
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
});

const labelsType = PropTypes.shape({
  createTeam: PropTypes.string.isRequired,
  current: PropTypes.string.isRequired,
  currentTeamDetail: PropTypes.string.isRequired,
  homeAriaLabel: PropTypes.string.isRequired,
  logout: PropTypes.string.isRequired,
  noTeam: PropTypes.string.isRequired,
  pageMenu: PropTypes.string.isRequired,
  pageSwitch: PropTypes.string.isRequired,
  settings: PropTypes.string.isRequired,
  teamMenu: PropTypes.string.isRequired,
  teamSelect: PropTypes.string.isRequired,
  userMenu: PropTypes.string.isRequired,
});

TopbarView.propTypes = {
  currentPage: pageItemType.isRequired,
  currentTeam: teamItemType,
  labels: labelsType.isRequired,
  languageSwitcher: PropTypes.node.isRequired,
  onCreateTeam: PropTypes.func.isRequired,
  onLogout: PropTypes.func.isRequired,
  onOpenAccountSettings: PropTypes.func.isRequired,
  onSelectHome: PropTypes.func.isRequired,
  onSelectPage: PropTypes.func.isRequired,
  onSelectTeam: PropTypes.func.isRequired,
  pageItems: PropTypes.arrayOf(pageItemType).isRequired,
  teamItems: PropTypes.arrayOf(teamItemType).isRequired,
};

TopbarView.defaultProps = {
  currentTeam: null,
};
