import { Paper, Tooltip } from "@mui/material";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React from "react";

import { threatImpactName, threatImpactProps } from "../utils/const";

export function ThreatImpactStatusChip(props) {
  const { statusCounts, threatImpact } = props;
  const impactName =
    threatImpact === 4 && statusCounts["completed"] > 0 ? "safe" : threatImpactName[threatImpact];
  const Icon = threatImpactProps[impactName].icon;

  const StyledTooltip = styled((styledProps) => (
    <Tooltip classes={{ popper: styledProps.className }} {...styledProps} />
  ))`
    & .MuiTooltip-tooltip {
      background-color: ${threatImpactProps[impactName].style.bgcolor};
      color: ${threatImpactProps[impactName].style.color};
    }
  `;

  return (
    <StyledTooltip title={threatImpactProps[impactName].statusLabel}>
      <Paper
        variant="outlined"
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "4px",
          ...threatImpactProps[impactName].style,
        }}
      >
        <Icon style={{ color: "white", fontSize: "20px" }} />
      </Paper>
    </StyledTooltip>
  );
}

ThreatImpactStatusChip.propTypes = {
  statusCounts: PropTypes.object,
  threatImpact: PropTypes.number.isRequired,
};
