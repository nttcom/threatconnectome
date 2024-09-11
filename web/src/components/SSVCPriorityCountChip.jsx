import { Box, Paper, Tooltip, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { ssvcPriorityProps } from "../utils/const";

const countMax = 99;

export function SSVCPriorityCountChip(props) {
  const { count, ssvcPriority, reverse, sx, outerSx } = props;

  const Icon = ssvcPriorityProps[ssvcPriority].icon;
  const baseSx = ssvcPriorityProps[ssvcPriority].style;
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
            <Typography id={"ssvc-priority-count-chip-" + ssvcPriority}>{countMax}+</Typography>
          </Tooltip>
        ) : (
          <Typography id={"ssvc-priority-count-chip-" + ssvcPriority}>{count}</Typography>
        )}
      </Paper>
    </Box>
  );
}

SSVCPriorityCountChip.propTypes = {
  ssvcPriority: PropTypes.string.isRequired,
  count: PropTypes.number.isRequired,
  reverse: PropTypes.bool,
  sx: PropTypes.object,
  outerSx: PropTypes.object,
};
SSVCPriorityCountChip.defaultProps = {
  reverse: false,
};