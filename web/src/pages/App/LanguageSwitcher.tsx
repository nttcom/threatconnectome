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

export function LanguageSwitcher() {
  const { t, i18n } = useTranslation("app", { keyPrefix: "LanguageSwitcher" });
  const currentLanguage = i18n.language;
  const [lang, setLang] = useState<string>(currentLanguage);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  return (
    <>
      {isMobile ? (
        <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ color: "text.primary" }}>
          <LanguageIcon />
        </IconButton>
      ) : (
        <Button
          variant="outlined"
          color="inherit"
          onClick={(e) => setAnchorEl(e.currentTarget)}
          startIcon={<LanguageIcon />}
          endIcon={<ArrowDropDownIcon />}
          sx={{ color: "text.primary" }}
        >
          {t("language")} {lang}
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
