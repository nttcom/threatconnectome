import { TablePagination } from "@mui/material";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { TopicTableRow } from "./TopicTableRow";

export function TopicTable(props) {
  const { pteamId, serviceId, tagId, topicIds, references } = props;
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [page, setPage] = useState(0);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const visibleTopicIds = topicIds.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

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
            {visibleTopicIds.map((topicId) => (
              <TopicTableRow
                key={topicId}
                pteamId={pteamId}
                serviceId={serviceId}
                tagId={tagId}
                topicId={topicId}
                references={references}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={topicIds.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
}
TopicTable.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  tagId: PropTypes.string.isRequired,
  topicIds: PropTypes.array.isRequired,
  references: PropTypes.array.isRequired,
};
