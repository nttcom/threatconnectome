import { ExpandLess, ExpandMore } from "@mui/icons-material";
import { Button } from "@mui/material";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

export function SmsTroubleshootingToggleButton({ expanded, onToggle, disabled }) {
  const { t } = useTranslation("components", { keyPrefix: "SmsTroubleshootingToggleButton" });

  return (
    <Button
      size="small"
      variant="text"
      onClick={onToggle}
      disabled={disabled}
      sx={{
        minWidth: 0,
        p: 0,
        alignItems: "center",
        display: "inline-flex",
        flexBasis: "100%",
        justifyContent: "flex-start",
        "& .MuiButton-startIcon": { marginRight: 0.5 },
      }}
      startIcon={expanded ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
    >
      {expanded ? t("hide") : t("view")}
    </Button>
  );
}

SmsTroubleshootingToggleButton.propTypes = {
  expanded: PropTypes.bool.isRequired,
  onToggle: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

SmsTroubleshootingToggleButton.defaultProps = {
  disabled: false,
};
