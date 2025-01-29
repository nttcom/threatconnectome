import { TablePagination } from "@mui/material";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import React, { useState } from "react";

import { TopicTableRow } from "./TopicTableRow";

const rows = [
  {
    title:
      "urllib3: proxy-authorization request header is not stripped during cross-origin redirects",
    lastUpdated: "2024-07-04T16:49:02+09:00",
    tickets: [
      {
        target: "api/Pipfile.lock",
        dueDate: "2025-01-22T00:00:00+09:00",
      },
      {
        target: "e2etests/Pipfile.lock",
      },
      {
        target: "scripts/Pipfile.lock",
      },
    ],
  },
];

export function TopicTable() {
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [page, setPage] = useState(0);
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const visibleRows = rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  return (
    <Paper elevation={3}>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell />
              <TableCell sx={{ fontWeight: "bold" }}>Title</TableCell>
              <TableCell sx={{ fontWeight: "bold" }} align="center">
                Ticket qty
              </TableCell>
              <TableCell sx={{ fontWeight: "bold" }} align="center">
                Last updated
              </TableCell>
              <TableCell sx={{ fontWeight: "bold" }} align="center">
                Affected version
              </TableCell>
              <TableCell sx={{ fontWeight: "bold" }} align="center">
                Patched version
              </TableCell>
              <TableCell />
            </TableRow>
          </TableHead>
          <TableBody>
            {visibleRows.map((row) => (
              <TopicTableRow key={row.title} row={row} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
}
