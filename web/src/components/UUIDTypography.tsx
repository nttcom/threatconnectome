import { Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import type { ComponentProps } from "react";

type UUIDTypographyProps = ComponentProps<typeof Typography>;

export function UUIDTypography(props: UUIDTypographyProps) {
  const { children, ...others } = props;

  return (
    <Typography color={grey[400]} variant="caption" {...others}>
      {children}
    </Typography>
  );
}
