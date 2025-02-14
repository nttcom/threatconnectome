import { Table, TableBody, TableCell, TableHead, TableRow } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { TicketTableRow } from "./TicketTableRow";

export function TicketTable(props) {
  const { tickets } = props;

  return (
    <Table size="small" sx={{ m: 1 }}>
      <TableHead>
        <TableRow>
          <TableCell sx={{ fontWeight: "bold" }}>Target</TableCell>
          <TableCell sx={{ fontWeight: "bold" }}>Safety Impact</TableCell>
          <TableCell sx={{ fontWeight: "bold" }}>Status</TableCell>
          <TableCell sx={{ fontWeight: "bold" }}>Due date</TableCell>
          <TableCell sx={{ fontWeight: "bold" }}>Assignees</TableCell>
          <TableCell sx={{ fontWeight: "bold" }} align="center">
            SSVC
          </TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {tickets.map((ticket) => (
          <TicketTableRow key={ticket.target} ticket={ticket} />
        ))}
      </TableBody>
    </Table>
  );
}

TicketTable.propTypes = {
  tickets: PropTypes.array,
};
