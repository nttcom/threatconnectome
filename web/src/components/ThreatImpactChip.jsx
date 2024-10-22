import { Chip } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { threatImpactNames, threatImpactProps } from "../utils/const";

export function ThreatImpactChip(props) {
  const { threatImpact, reverse = false, sx } = props;

  const impactName = Object.keys(threatImpactProps).includes(threatImpact)
    ? threatImpact
    : threatImpactNames[threatImpact];
  const baseStyle = threatImpactProps[impactName].style;
  const fixedSx = {
    ...(reverse
      ? {
          ...baseStyle,
          color: baseStyle.bgcolor,
          bgcolor: baseStyle.color,
          borderColor: baseStyle.bgcolor,
        }
      : baseStyle),
    ...sx,
  };

  return (
    <Chip
      label={threatImpactProps[impactName].chipLabel}
      variant={reverse ? "outlined" : "filled"}
      sx={fixedSx}
    />
  );
}

ThreatImpactChip.propTypes = {
  threatImpact: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  reverse: PropTypes.bool,
  sx: PropTypes.object,
};
