import { Chip } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { threatImpactName, threatImpactProps } from "../utils/const";

export default function ThreatImpactChip(props) {
  const { threatImpact, reverse, sx } = props;

  const impactName = Object.keys(threatImpactProps).includes(threatImpact)
    ? threatImpact
    : threatImpactName[threatImpact];
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
ThreatImpactChip.defaultProps = {
  reverse: false,
};
