import { Box, TableCell, TableRow, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";

import { APIError } from "../../utils/APIError";

export function PTeamStatusCardFallback({ error }) {
  console.log(error);
  return (
    <TableRow
      sx={{
        cursor: "pointer",
        "&:last-child td, &:last-child th": { border: 0 },
        "&:hover": { bgcolor: grey[100] },
      }}
    >
      <TableCell colSpan={1000}>
        <Box>
          <Typography>Error occurred at PTeamStatusCard: {error.message}</Typography>
          {error instanceof APIError && (
            <Typography>called API: {error.api || "unknown"}</Typography>
          )}
        </Box>
      </TableCell>
    </TableRow>
  );
}
PTeamStatusCardFallback.propTypes = {
  error: PropTypes.object.isRequired,
};
