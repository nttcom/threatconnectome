import { Paper, Tooltip } from "@mui/material";
import { useTranslation } from "react-i18next";

import { getSsvcPriorityProps } from "../utils/ssvcUtils";

type SSVCPriorityStatusChipProps = {
  displaySSVCPriority: keyof ReturnType<typeof getSsvcPriorityProps>;
};

export function SSVCPriorityStatusChip(props: SSVCPriorityStatusChipProps) {
  const { displaySSVCPriority } = props;
  // Calling useTranslation() ensures this component re-renders when the language changes.
  useTranslation();

  const ssvcPriorityProps = getSsvcPriorityProps();
  const ssvcPriorityProp = ssvcPriorityProps[displaySSVCPriority];

  const Icon = ssvcPriorityProp.icon;

  return (
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
    </Tooltip>
  );
}
