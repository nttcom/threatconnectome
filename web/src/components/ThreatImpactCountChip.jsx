import { Box, Paper, Tooltip, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { threatImpactName, threatImpactProps } from "../utils/const";

const countMax = 99;

export function ThreatImpactCountChip(props) {
  const { count, threatImpact, reverse, sx, outerSx } = props;

  const impactName = Object.keys(threatImpactProps).includes(threatImpact)
    ? threatImpact
    : threatImpactName[threatImpact];
  const Icon = threatImpactProps[impactName].icon;
  const baseSx = threatImpactProps[impactName].style;
  const fixedSx = {
    ...baseSx,
    ...sx,
    borderColor: baseSx.bgcolor,
    ...(reverse && {
      color: baseSx.bgcolor,
      bgcolor: baseSx.color,
    }),
    display: "flex",
    alignItems: "baseline",
    justifyContent: "center",
    padding: "4px",
    height: "30px",
  };

  return (
    <Box display="flex" sx={outerSx}>
      <Paper
        variant="outlined"
        sx={{
          ...fixedSx,
          borderRightWidth: "0",
          borderTopRightRadius: "0",
          borderBottomRightRadius: "0",
        }}
      >
        <Icon style={{ fontSize: "20px" }} />
      </Paper>
      <Paper
        variant="outlined"
        sx={{
          ...fixedSx,
          borderLeftWidth: "0",
          borderTopLeftRadius: "0",
          borderBottomLeftRadius: "0",
          width: "35px",
          color: reverse ? "lightgray" : "black",
          bgcolor: "white",
        }}
      >
        {count > countMax ? (
          <Tooltip title={count}>
            <Typography id={"threat-impact-count-chip-" + threatImpact}>{countMax}+</Typography>
          </Tooltip>
        ) : (
          <Typography id={"threat-impact-count-chip-" + threatImpact}>{count}</Typography>
        )}
      </Paper>
    </Box>
  );
}

ThreatImpactCountChip.propTypes = {
  threatImpact: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  count: PropTypes.number.isRequired,
  reverse: PropTypes.bool,
  sx: PropTypes.object,
  outerSx: PropTypes.object,
};
ThreatImpactCountChip.defaultProps = {
  reverse: false,
};
