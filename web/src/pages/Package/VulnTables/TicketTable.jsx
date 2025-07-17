import { Table, TableBody, TableCell, TableHead, TableRow } from "@mui/material";
import PropTypes from "prop-types";

export function TicketTable(props) {
  const { children } = props;

  return (
    <Table size="small" sx={{ m: 1 }}>
      <TableHead>
        <TableRow>
          <TableCell sx={{ fontWeight: "bold" }}>Target</TableCell>
          <TableCell align="center" sx={{ fontWeight: "bold" }}>
            Package manager
          </TableCell>
          <TableCell sx={{ fontWeight: "bold" }}>Safety Impact</TableCell>
          <TableCell sx={{ fontWeight: "bold" }}>Status</TableCell>
          <TableCell sx={{ fontWeight: "bold" }}>Due date</TableCell>
          <TableCell sx={{ fontWeight: "bold" }}>Assignees</TableCell>
          <TableCell sx={{ fontWeight: "bold" }} align="center">
            SSVC
          </TableCell>
        </TableRow>
      </TableHead>
      <TableBody>{children}</TableBody>
    </Table>
  );
}

TicketTable.propTypes = {
  children: PropTypes.array,
};
