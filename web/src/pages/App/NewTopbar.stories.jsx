import "@fontsource/inter/700.css";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import CheckIcon from "@mui/icons-material/Check";
import ChecklistIcon from "@mui/icons-material/Checklist";
import EventNoteIcon from "@mui/icons-material/EventNote";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import GppMaybeIcon from "@mui/icons-material/GppMaybe";
import GroupIcon from "@mui/icons-material/Group";
import Inventory2Icon from "@mui/icons-material/Inventory2";
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
import { useState } from "react";

// ---------------------------------------------------------------------------
// Design Tokens
// ---------------------------------------------------------------------------

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
  red700: "#B91C1C",
  amber50: "#FFFBEB",
  amber100: "#FEF3C7",
  amber600: "#D97706",
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

// ---------------------------------------------------------------------------
// Shared sx presets
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Fixture Data
// ---------------------------------------------------------------------------

const user = {
  initials: "YA",
  name: "Yuki Admin",
  email: "admin@threatconnectome.example",
};

const pageItems = [
  {
    label: "SBOM管理",
    shortLabel: "SBOM",
    icon: Inventory2Icon,
    tone: "brand",
  },
  {
    label: "チーム管理",
    icon: GroupIcon,
    tone: "sky",
  },
  {
    label: "脆弱性",
    icon: GppMaybeIcon,
    tone: "red",
  },
  {
    label: "EOL",
    icon: EventNoteIcon,
    tone: "amber",
  },
  {
    label: "TODO",
    icon: ChecklistIcon,
    tone: "violet",
  },
];

const teamItems = [
  { name: "Security Team", current: true },
  { name: "Platform Team" },
  { name: "Product Team" },
  { name: "Backend Team" },
  { name: "Frontend Team" },
  { name: "SRE Team" },
  { name: "Incident Response Team" },
  { name: "Cloud Infrastructure Team" },
  { name: "Identity Access Team" },
  { name: "Compliance Team" },
  { name: "DevSecOps Team" },
  { name: "Data Protection Team" },
  { name: "Mobile App Team" },
  { name: "Partner Integration Team" },
];

const currentTeam = teamItems.find((item) => item.current);

// ---------------------------------------------------------------------------
// Hooks
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

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

function CurrentChip({ sx }) {
  return (
    <Chip
      label="現在"
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

// ---------------------------------------------------------------------------
// Logo
// ---------------------------------------------------------------------------

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
          letterSpacing: "-0.01em",
          lineHeight: 1,
          userSelect: "none",
        }}
      >
        Threatconnectome
      </Typography>
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Menu Shell & Header (shared by all menus)
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Page Menu
// ---------------------------------------------------------------------------

function PageMenuItem({ current, item, onSelect }) {
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
          {current ? <CurrentChip sx={{ bgcolor: "#fff" }} /> : null}
        </Stack>
      </Box>
    </MenuItem>
  );
}

function PageMenu({ anchorEl, currentPage, open, onClose, onSelectPage }) {
  return (
    <MenuShell
      anchorEl={anchorEl}
      ariaLabel="ページ切替"
      open={open}
      onClose={onClose}
      width={menuWidths.page}
    >
      <MenuHeader title="ページ切替" />
      {pageItems.map((item) => (
        <PageMenuItem
          key={item.label}
          current={item.label === currentPage.label}
          item={item}
          onSelect={onSelectPage}
        />
      ))}
    </MenuShell>
  );
}

// ---------------------------------------------------------------------------
// Team Menu
// ---------------------------------------------------------------------------

function TeamMenuItem({ item, onClose }) {
  return (
    <MenuItem
      onClick={onClose}
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

function TeamMenuList({ onClose }) {
  return (
    <Box sx={teamMenuListSx}>
      {teamItems.map((item) => (
        <TeamMenuItem key={item.name} item={item} onClose={onClose} />
      ))}
    </Box>
  );
}

function TeamMenu({ anchorEl, open, onClose }) {
  return (
    <MenuShell
      anchorEl={anchorEl}
      ariaLabel="チーム選択"
      open={open}
      onClose={onClose}
      width={menuWidths.default}
    >
      <MenuHeader title="チーム選択" />
      <TeamMenuList onClose={onClose} />
    </MenuShell>
  );
}

// ---------------------------------------------------------------------------
// User Menu (mimics the existing UserMenu component)
// ---------------------------------------------------------------------------

function UserMenu({ anchorEl, open, onClose }) {
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
      {isMobile ? (
        <>
          <MenuHeader title="チーム選択" detail="現在のチームを切り替え" />
          <TeamMenuList onClose={onClose} />
          <Divider sx={{ my: 0.75 }} />
        </>
      ) : null}
      <MenuItem onClick={onClose} sx={isMobile ? compactMenuItemSx : undefined}>
        <ListItemIcon>
          <SettingsIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>設定</ListItemText>
      </MenuItem>
      <Divider sx={isMobile ? { my: 0.75 } : undefined} />
      <MenuItem onClick={onClose} sx={isMobile ? compactMenuItemSx : undefined}>
        <ListItemIcon>
          <LogoutIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>ログアウト</ListItemText>
      </MenuItem>
    </Menu>
  );
}

// ---------------------------------------------------------------------------
// Topbar Buttons
// ---------------------------------------------------------------------------

function TopbarLogoLink() {
  return (
    <Box
      component="a"
      href="#"
      aria-label="Threatconnectome home"
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

function PageMenuButton({ active, currentPage, onClick }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  if (isMobile) {
    return (
      <MenuTriggerButton
        active={active}
        ariaLabel="ページメニュー"
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
      ariaLabel="ページメニュー"
      onClick={onClick}
      sx={{
        ...responsiveTopbarButtonSx,
        maxWidth: { sm: 220 },
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
          sx={{ display: { xs: "none", sm: "block" }, fontSize: 14, fontWeight: 600 }}
        >
          {currentPage.label}
        </Typography>
        <Box sx={{ color: colors.ink400 }}>
          <IconRenderer icon={ExpandMoreIcon} size={16} />
        </Box>
      </Stack>
    </MenuTriggerButton>
  );
}

function TeamMenuButton({ active, onClick }) {
  return (
    <MenuTriggerButton
      active={active}
      ariaLabel="チームメニュー"
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
          {currentTeam.name}
        </Typography>
        <Box sx={{ display: { xs: "none", sm: "flex" }, color: colors.ink400 }}>
          <IconRenderer icon={ExpandMoreIcon} size={16} />
        </Box>
      </Stack>
    </MenuTriggerButton>
  );
}

function UserMenuButton({ active, onClick }) {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const userIcon = <IconRenderer icon={AccountCircleIcon} size={22} />;

  if (isDesktop) {
    return (
      <Button
        aria-label="user menu"
        aria-haspopup="menu"
        aria-expanded={active}
        onClick={onClick}
        startIcon={<AccountCircleIcon />}
        sx={{ maxWidth: 400 }}
      >
        <Typography variant="button" sx={ellipsisTextSx}>
          {user.email}
        </Typography>
      </Button>
    );
  }

  return (
    <MenuTriggerButton
      active={active}
      ariaLabel="user menu"
      onClick={onClick}
      sx={compactTopbarButtonSx}
    >
      {userIcon}
    </MenuTriggerButton>
  );
}

// ---------------------------------------------------------------------------
function ThreatconnectomeTopbarMuiStory() {
  const { anchorEl, close, toggle, isOpen } = useMenu();
  const [currentPage, setCurrentPage] = useState(pageItems[0]);

  const selectPage = (item) => {
    setCurrentPage(item);
    close();
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#fff", color: colors.ink900 }}>
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
            gridTemplateColumns: { xs: "40px 1fr 48px", sm: "none" },
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
            <TopbarLogoLink />
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
              onClick={toggle("page")}
            />
          </Stack>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "start" }}>
            <PageMenuButton
              active={isOpen("page")}
              currentPage={currentPage}
              onClick={toggle("page")}
            />
          </Box>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "center" }}>
            <TopbarLogoLink />
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
            <TeamMenuButton active={isOpen("team")} onClick={toggle("team")} />
            <UserMenuButton active={isOpen("user")} onClick={toggle("user")} />
          </Stack>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "end" }}>
            <UserMenuButton active={isOpen("user")} onClick={toggle("user")} />
          </Box>
        </Toolbar>
      </AppBar>

      <PageMenu
        anchorEl={anchorEl}
        currentPage={currentPage}
        open={isOpen("page")}
        onClose={close}
        onSelectPage={selectPage}
      />
      <TeamMenu anchorEl={anchorEl} open={isOpen("team")} onClose={close} />
      <UserMenu anchorEl={anchorEl} open={isOpen("user")} onClose={close} />
    </Box>
  );
}

// ---------------------------------------------------------------------------
// Storybook Meta
// ---------------------------------------------------------------------------

const meta = {
  title: "Threatconnectome/Topbar MUI",
  component: ThreatconnectomeTopbarMuiStory,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

export const Default = {
  render: () => <ThreatconnectomeTopbarMuiStory />,
};
