import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TablePagination from "@mui/material/TablePagination";
import TableRow from "@mui/material/TableRow";
import PropTypes from "prop-types";
import { useState, useMemo, useEffect } from "react";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetTicketsQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { ssvcPriorityProps } from "../../utils/const";
import { errorToString, utcStringToLocalDate } from "../../utils/func";

import { ToDoTableRow } from "./ToDoTableRow";

export function ToDoTable({ myTasks, pteamIds, page, rowsPerPage, onPageChange }) {
  const skip = useSkipUntilAuthUserIsReady();

  const {
    data: tickets,
    error: ticketsError,
    isLoading: ticketsIsLoading,
  } = useGetTicketsQuery({
    pteamIds,
    offset: page * rowsPerPage,
    limit: rowsPerPage,
    sortKey: "ssvc_deployer_priority_desc",
    assignedToMe: myTasks,
    excludeStatuses: ["completed"],
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

  const handleChangePage = (event, newPage) => {
    onPageChange({ page: newPage });
  };

  const handleChangeRowsPerPage = (event) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    onPageChange({
      perPage: newRowsPerPage,
      page: 0, // reset page
    });
  };

  // useEffect(() => {
  //   setPage(0);
  // }, [myTasks]);

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
                <TableCell>CVE-ID</TableCell>
                <TableCell>Team</TableCell>
                <TableCell>Service</TableCell>
                <TableCell>Due date</TableCell>
                <TableCell>Assignee</TableCell>
                <TableCell>SSVC</TableCell>
                <TableCell />
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
          page={page}
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
};
