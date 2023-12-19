import { Tooltip, Typography } from "@mui/material";
import { format } from "date-fns";
import PropTypes from "prop-types";
import React from "react";

import { utcStringToLocalDate } from "../utils/func";

export function FormattedDateTimeWithTooltip(props) {
  const { utcString, formatString, sx } = props;

  try {
    if (!utcString) throw new Error("empty string");
    const localDate = utcStringToLocalDate(utcString);
    const tipTitle = localDate.toISOString();
    const formattedDate = format(localDate, formatString);
    return (
      <Tooltip title={tipTitle}>
        <Typography sx={{ overflowWrap: "anywhere", ...sx }}>{formattedDate}</Typography>
      </Tooltip>
    );
  } catch (error) {
    return <Typography sx={{ overflowWrap: "anywhere", ...sx }}> - </Typography>;
  }
}
FormattedDateTimeWithTooltip.propTypes = {
  utcString: PropTypes.string,
  formatString: PropTypes.string,
  sx: PropTypes.object,
};
FormattedDateTimeWithTooltip.defaultProps = {
  formatString: "PPp", // see https://date-fns.org/v3.0.0/docs/format for details
};
