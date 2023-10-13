import { Star as StarIcon } from "@mui/icons-material";
import { Box, Tooltip } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

export default function RecommendedStar(props) {
  const { disabled, sx } = props;

  return (
    <Box sx={{ mr: 1, ...sx }}>
      {disabled ? (
        <StarIcon color="disabled" />
      ) : (
        <Tooltip arrow placement="bottom" title="recommended">
          <StarIcon color="warning" />
        </Tooltip>
      )}
    </Box>
  );
}

RecommendedStar.propTypes = {
  disabled: PropTypes.bool.isRequired,
  sx: PropTypes.object,
};
