import { Box } from "@mui/material";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TablePagination from "@mui/material/TablePagination";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import { visuallyHidden } from "@mui/utils";
import PropTypes from "prop-types";
import { useState, useMemo } from "react";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetTicketsQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { ssvcPriorityProps } from "../../utils/const";
import { errorToString, utcStringToLocalDate } from "../../utils/func";

import { ToDoTableRow } from "./ToDoTableRow";

export function ToDoTable({
  myTasks,
  pteamIds,
  cveIds,
  page,
  rowsPerPage,
  onPageChange,
  sortKey,
  sortDirection,
}) {
  const skip = useSkipUntilAuthUserIsReady();

  const {
    data: tickets,
    error: ticketsError,
    isLoading: ticketsIsLoading,
  } = useGetTicketsQuery({
    pteamIds,
    offset: (page - 1) * rowsPerPage,
    limit: rowsPerPage,
    sortKeys: [sortDirection === "asc" ? sortKey : `-${sortKey}`, "-created_at"],
    assignedToMe: myTasks,
    excludeStatuses: ["completed"],
    cveIds: cveIds,
  });

  const rows = useMemo(() => {
    const hasAssignees = (ticketStatus) => ticketStatus?.assignees?.length > 0;

    const allTickets = tickets?.tickets ?? [];
    return allTickets.map((ticket) => ({
      ticket_id: ticket.ticket_id,
      vuln_id: ticket.vuln_id || "-",
      service_id: ticket.service_id,
      dueDate: ticket.ticket_status?.scheduled_at
        ? (() => {
            const formattedDate = utcStringToLocalDate(ticket.ticket_status.scheduled_at, false);
            return formattedDate || "-";
          })()
        : "-",
      assignee: hasAssignees(ticket.ticket_status) ? ticket.ticket_status.assignees : "-",
      ssvc: ticket.ssvc_deployer_priority,
      pteam_id: ticket.pteam_id,
      dependency_id: ticket.dependency_id,
      ticket_safety_impact: ticket.ticket_safety_impact,
      ticket_safety_impact_change_reason: ticket.ticket_safety_impact_change_reason,
      ticket_status: ticket.ticket_status,
    }));
  }, [tickets]);

  const handleRequestSort = (event, property) => {
    const isAsc = sortKey === property && sortDirection === "asc"; // Determines if the column currently in ascending order is clicked again
    const newDirection = isAsc ? "desc" : "asc";
    if (page >= 2){
      onPageChange({ sortKey: property, sortDirection: newDirection, page: 1 }) // Reset to first page if sorting changes after page 2.
    }else{
      onPageChange({ sortKey: property, sortDirection: newDirection });
    }
  };

  const handleChangePage = (event, newPage) => {
    onPageChange({ page: newPage + 1 });
  };

  const handleChangeRowsPerPage = (event) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    onPageChange({
      perPage: newRowsPerPage,
      page: 1, // reset page
    });
  };

  const headCells = [
    { id: "cve_id", label: "CVE", isSortable: true },
    { id: "pteam_name", label: "Team", isSortable: true },
    { id: "service_name", label: "Service", isSortable: true },
    { id: "package_name", label: "Package", isSortable: true },
    { id: "assignee", label: "Assignee", isSortable: false },
    { id: "ssvc_deployer_priority", label: "SSVC", isSortable: true },
  ];

  if (skip) return <></>;
  if (ticketsError) throw new APIError(errorToString(ticketsError), { api: "getTickets" });
  if (ticketsIsLoading) return <>Now loading Tickets...</>;

  return (
    <Paper sx={{ width: "100%" }} variant="outlined">
      <>
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
              {rows.map((row, idx) => {
                const ssvcPriority = ssvcPriorityProps[row.ssvc] || ssvcPriorityProps["defer"];
                return (
                  <ToDoTableRow
                    key={row.ticket_id}
                    row={row}
                    ssvcPriority={ssvcPriority}
                    vuln_id={row.vuln_id}
                  />
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 20, 50, 100]}
          component="div"
          count={tickets?.total ?? 0}
          rowsPerPage={rowsPerPage}
          page={page - 1}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          showFirstButton
          showLastButton
        />
      </>
    </Paper>
  );
}

ToDoTable.propTypes = {
  myTasks: PropTypes.bool.isRequired,
  pteamIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  page: PropTypes.number.isRequired,
  rowsPerPage: PropTypes.number.isRequired,
  onPageChange: PropTypes.func.isRequired,
  cveIds: PropTypes.arrayOf(PropTypes.string),
  sortKey: PropTypes.string.isRequired,
  sortDirection: PropTypes.string.isRequired,
};
