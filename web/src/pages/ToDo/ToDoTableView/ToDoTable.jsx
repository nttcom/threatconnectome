import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  Typography,
} from "@mui/material";
import { visuallyHidden } from "@mui/utils";
import PropTypes from "prop-types";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useGetTicketsQuery } from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { ssvcPriorityProps } from "../../../utils/ssvcUtils";
import { errorToString } from "../../../utils/func";

import { ToDoTableRow } from "./ToDoTableRow";

export function ToDoTable({
  pteamIds,
  apiParams,
  onSortConfigChange,
  onPageChange,
  onItemsPerPageChange,
}) {
  const skip = useSkipUntilAuthUserIsReady();

  const {
    data: ticketsData,
    error: ticketsError,
    isLoading: ticketsIsLoading,
  } = useGetTicketsQuery({
    query: { ...apiParams, pteam_ids: pteamIds },
  });

  const tickets = ticketsData?.tickets ?? [];

  const { page, limit: rowsPerPage } = apiParams;
  const { key: sortKey, direction: sortDirection } = apiParams.sortConfig || {};

  const handleRequestSort = (event, property) => {
    const isAsc = sortKey === property && sortDirection === "asc"; // Determines if the column currently in ascending order is clicked again
    const newDirection = isAsc ? "desc" : "asc";
    onSortConfigChange({ key: property, direction: newDirection });
  };

  const handleChangePage = (event, newPage) => {
    onPageChange(event, newPage + 1);
  };

  const handleChangeRowsPerPage = (event) => {
    onItemsPerPageChange(event.target.value);
  };

  const headCells = [
    { id: "cve_id", label: "CVE", isSortable: true },
    { id: "pteam_name", label: "Team", isSortable: true },
    { id: "service_name", label: "Service", isSortable: true },
    { id: "package_name", label: "Package", isSortable: true },
    { id: "assignee", label: "Assignee", isSortable: false },
    { id: "ssvc_deployer_priority", label: "SSVC", isSortable: true },
    { id: "details", label: "", isSortable: false },
  ];

  if (skip) return <></>;
  if (ticketsError) throw new APIError(errorToString(ticketsError), { api: "getTickets" });
  if (ticketsIsLoading) return <>Now loading Tickets...</>;

  return (
    <Paper sx={{ width: "100%" }} variant="outlined">
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              {headCells.map((headCell) => (
                <TableCell
                  key={headCell.id}
                  sortDirection={sortKey === headCell.id ? sortDirection : false}
                >
                  {headCell.isSortable ? (
                    <TableSortLabel
                      active={sortKey === headCell.id}
                      direction={sortKey === headCell.id ? sortDirection : "asc"}
                      onClick={(event) => handleRequestSort(event, headCell.id)}
                    >
                      {headCell.label}
                      {sortKey === headCell.id ? (
                        <Box component="span" sx={visuallyHidden}>
                          {sortDirection === "desc" ? "sorted descending" : "sorted ascending"}
                        </Box>
                      ) : null}
                    </TableSortLabel>
                  ) : (
                    headCell.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {tickets.length > 0 ? (
              tickets.map((ticket) => {
                const ssvcPriority =
                  ssvcPriorityProps[ticket.ssvc_deployer_priority] || ssvcPriorityProps["defer"];
                return (
                  <ToDoTableRow
                    key={ticket.ticket_id}
                    ticket={ticket}
                    ssvcPriority={ssvcPriority}
                  />
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={headCells.length} align="center">
                  <Typography color="text.secondary" sx={{ py: 5 }}>
                    No tasks found.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 20, 50, 100]}
        component="div"
        count={ticketsData?.total ?? 0}
        rowsPerPage={rowsPerPage}
        page={page - 1}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        showFirstButton
        showLastButton
      />
    </Paper>
  );
}

ToDoTable.propTypes = {
  pteamIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  apiParams: PropTypes.object.isRequired,
  onSortConfigChange: PropTypes.func.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onItemsPerPageChange: PropTypes.func.isRequired,
};
