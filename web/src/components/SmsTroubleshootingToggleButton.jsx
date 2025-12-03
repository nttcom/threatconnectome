import { ExpandLess, ExpandMore } from "@mui/icons-material";
import { Button } from "@mui/material";
import PropTypes from "prop-types";

export function SmsTroubleshootingToggleButton({ expanded, onToggle, disabled }) {
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
      {expanded ? "Hide troubleshooting tips" : "View troubleshooting tips"}
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
