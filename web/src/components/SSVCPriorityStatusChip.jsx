import { Paper, Tooltip } from "@mui/material";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";

import { ssvcPriorityProps } from "../utils/ssvcUtils";

export function SSVCPriorityStatusChip(props) {
  const { displaySSVCPriority } = props;
  const ssvcPriorityProp = ssvcPriorityProps[displaySSVCPriority];

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
          width: 30,
          height: 30,
          ...ssvcPriorityProp.style,
        }}
      >
        <Icon style={{ color: "white", fontSize: "20px" }} />
      </Paper>
    </StyledTooltip>
  );
}

SSVCPriorityStatusChip.propTypes = {
  displaySSVCPriority: PropTypes.string.isRequired,
};
