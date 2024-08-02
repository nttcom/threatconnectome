import { Paper, Tooltip } from "@mui/material";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React from "react";

import { threatImpactProps } from "../utils/const";

export function ThreatImpactStatusChip(props) {
  const { threatImpactName } = props;
  const Icon = threatImpactProps[threatImpactName].icon;

  const StyledTooltip = styled((styledProps) => (
    <Tooltip classes={{ popper: styledProps.className }} {...styledProps} />
  ))`
    & .MuiTooltip-tooltip {
      background-color: ${threatImpactProps[threatImpactName].style.bgcolor};
      color: ${threatImpactProps[threatImpactName].style.color};
    }
  `;

  return (
    <StyledTooltip title={threatImpactProps[threatImpactName].statusLabel}>
      <Paper
        variant="outlined"
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "4px",
          ...threatImpactProps[threatImpactName].style,
        }}
      >
        <Icon style={{ color: "white", fontSize: "20px" }} />
      </Paper>
    </StyledTooltip>
  );
}

ThreatImpactStatusChip.propTypes = {
  threatImpactName: PropTypes.string.isRequired,
};
