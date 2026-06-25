import { Box } from "@mui/material";
import type { HTMLAttributes, ReactNode } from "react";

type CustomTabPanelProps = HTMLAttributes<HTMLDivElement> & {
  children?: ReactNode;
  index: number;
  value: number;
};

export function CustomTabPanel(props: CustomTabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}
