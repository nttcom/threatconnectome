import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import CheckIcon from "@mui/icons-material/Check";
import LanguageIcon from "@mui/icons-material/Language";
import {
  Button,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export function LanguageSwitcher({ compact = true }: { compact?: boolean }) {
  const { i18n } = useTranslation();
  const lang = i18n.language;
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  return (
    <>
      {compact && isMobile ? (
        <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ color: "text.secondary" }}>
          <LanguageIcon />
        </IconButton>
      ) : (
        <Button
          variant="outlined"
          onClick={(e) => setAnchorEl(e.currentTarget)}
          startIcon={<LanguageIcon />}
          endIcon={<ArrowDropDownIcon />}
          size="small"
          sx={{ bgcolor: "background.subtle", borderColor: "divider", color: "text.primary" }}
        >
          {lang}
        </Button>
      )}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
        <MenuItem
          onClick={() => {
            setAnchorEl(null);
            i18n.changeLanguage("en");
          }}
        >
          <ListItemIcon>
            {lang === "en" && <CheckIcon color="success" fontSize="small" />}
          </ListItemIcon>
          <ListItemText>English</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => {
            setAnchorEl(null);
            i18n.changeLanguage("ja");
          }}
        >
          <ListItemIcon>
            {lang === "ja" && <CheckIcon color="success" fontSize="small" />}
          </ListItemIcon>
          <ListItemText>日本語</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
}
