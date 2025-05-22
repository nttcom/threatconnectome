import { Chip } from "@mui/material";
import PropTypes from "prop-types";

import { actionTypeChipColors, actionTypeChipWidth } from "../../utils/const";

export function ActionTypeChip(props) {
  const { actionType, sx } = props;
  return (
    <Chip
      color={actionTypeChipColors[actionType]}
      label={actionType}
      variant="outlined"
      size="small"
      sx={{ flexShrink: 0, width: actionTypeChipWidth, ...sx }}
    />
  );
}

ActionTypeChip.propTypes = {
  actionType: PropTypes.string.isRequired,
  sx: PropTypes.object,
};
