import { Paper, Tooltip } from "@mui/material";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React from "react";

import { ssvcPriorityProps } from "../utils/const";

export function SSVCPriorityStatusChip(props) {
  const { ssvcPriority } = props;
  const ssvcPriorityProp = ssvcPriorityProps[ssvcPriority];

  const Icon = ssvcPriorityProp.icon;
  const StyledTooltip = styled((styledProps) => (
    <Tooltip classes={{ popper: styledProps.className }} {...styledProps} />
  ))`
    & .MuiTooltip-tooltip {
      background-color: ${ssvcPriorityProp.style.bgcolor};
      color: ${ssvcPriorityProp.style.color};
    }
  `;

  return (
    <StyledTooltip title={ssvcPriorityProp.statusLabel}>
      <Paper
        variant="outlined"
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "4px",
          ...ssvcPriorityProp.style,
        }}
      >
        <Icon style={{ color: "white", fontSize: "20px" }} />
      </Paper>
    </StyledTooltip>
  );
}

SSVCPriorityStatusChip.propTypes = {
  ssvcPriority: PropTypes.string.isRequired,
};
