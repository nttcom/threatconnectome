import { Tooltip, Typography } from "@mui/material";
import type { SxProps, Theme } from "@mui/material";
import { format } from "date-fns";

type FormattedDateTimeWithTooltipProps = {
  utcString?: string | null;
  formatString?: string;
  sx?: SxProps<Theme>;
};

export function FormattedDateTimeWithTooltip(props: FormattedDateTimeWithTooltipProps) {
  const { utcString, formatString = "PPp", sx } = props; // see https://date-fns.org/v3.0.0/docs/format for details
  const typographySx = [{ overflowWrap: "anywhere" }, ...(Array.isArray(sx) ? sx : [sx])];

  try {
    if (!utcString) throw new Error("empty string");
    const localDate = new Date(utcString);
    const tipTitle = localDate.toISOString();
    const formattedDate = format(localDate, formatString);
    return (
      <Tooltip title={tipTitle}>
        <Typography sx={typographySx}>{formattedDate}</Typography>
      </Tooltip>
    );
  } catch (error) {
    return <Typography sx={typographySx}> - </Typography>;
  }
}
