import { Box, Paper, Tooltip, Typography } from "@mui/material";

import { getSsvcPriorityProps } from "../../utils/ssvcUtils";
import type { SSVCPriorityCountChipProps } from "./PackagePageTypes";

const countMax = 99;

export function SSVCPriorityCountChip({
  count,
  ssvcPriority,
  reverse = false,
  sx,
  outerSx,
}: SSVCPriorityCountChipProps) {
  const ssvcPriorityProp = getSsvcPriorityProps()[ssvcPriority];

  const Icon = ssvcPriorityProp.icon;
  const baseSx = ssvcPriorityProp.style;
  const fixedSx = {
    ...baseSx,
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
      <Tooltip
        title={ssvcPriorityProp.statusLabel}
        slotProps={{
          tooltip: {
            sx: {
              backgroundColor: ssvcPriorityProp.style.bgcolor,
              color: ssvcPriorityProp.style.color,
            },
          },
        }}
      >
        <Paper
          variant="outlined"
          sx={[
            fixedSx,
            ...(Array.isArray(sx) ? sx : [sx]),
            {
              borderRightWidth: "0",
              borderTopRightRadius: "0",
              borderBottomRightRadius: "0",
            },
          ]}
        >
          <Icon style={{ fontSize: "20px" }} />
        </Paper>
      </Tooltip>
      <Paper
        variant="outlined"
        sx={[
          fixedSx,
          ...(Array.isArray(sx) ? sx : [sx]),
          {
            borderLeftWidth: "0",
            borderTopLeftRadius: "0",
            borderBottomLeftRadius: "0",
            width: "35px",
            color: reverse ? "lightgray" : "black",
            bgcolor: "white",
          },
        ]}
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
