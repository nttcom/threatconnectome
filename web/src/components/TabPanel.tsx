import { Box } from "@mui/material";
import type { ComponentProps, ReactNode } from "react";

type TabPanelProps = ComponentProps<typeof Box> & {
  children?: ReactNode;
  index: number;
  value: number;
};

export function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <Box
      aria-labelledby={`tab-${index}`}
      hidden={value !== index}
      id={`tab-panel-${index}`}
      m={2}
      role="tabpanel"
      {...other}
    >
      {value === index && children}
    </Box>
  );
}
