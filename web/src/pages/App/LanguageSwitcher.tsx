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
  const currentLanguage = i18n.language;
  const [lang, setLang] = useState<string>(currentLanguage);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  return (
    <>
      {compact && isMobile ? (
        <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ color: "#5f6368" }}>
          <LanguageIcon />
        </IconButton>
      ) : (
        <Button
          variant="outlined"
          onClick={(e) => setAnchorEl(e.currentTarget)}
          startIcon={<LanguageIcon />}
          endIcon={<ArrowDropDownIcon />}
          size="small"
          sx={{
            bgcolor: "#f8f9fa",
            borderColor: "#dadce0",
            color: "#3c4043",
            textTransform: "none",
            fontSize: 14,
          }}
        >
          {lang.toUpperCase()}
        </Button>
      )}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
        <MenuItem
          onClick={() => {
            setLang("en");
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
            setLang("ja");
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
