import { Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";

export function UUIDTypography(props) {
  const { children, ...others } = props;

  return (
    <Typography color={grey[400]} variant="caption" {...others}>
      {children}
    </Typography>
  );
}

UUIDTypography.propTypes = {
  children: PropTypes.node,
};
