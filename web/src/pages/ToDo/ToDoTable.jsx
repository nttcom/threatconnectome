import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableContainer from "@mui/material/TableContainer";
import TablePagination from "@mui/material/TablePagination";
import { amber, grey, orange, red } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useState, useEffect, useMemo } from "react";

import { useGetUserMeQuery } from "../../services/tcApi";

import { EnhancedTableHead } from "./EnhancedTableHead";
import { getComparator, useTicketsAndPteams } from "./ToDoTableFunc";
import { ToDoTableRow } from "./ToDoTableRow";

export function ToDoTable({ myTasks, pteamIds }) {
  const { data: me } = useGetUserMeQuery();
  const myUserId = me?.user_id;

  const [order, setOrder] = useState(() => localStorage.getItem("todoTableOrder") || "asc");
  const [orderBy, setOrderBy] = useState(() => localStorage.getItem("todoTableOrderBy") || "ssvc");

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const { allTickets, pteamMap, serviceMap, userMap, loading } = useTicketsAndPteams(
    pteamIds,
    false,
  );
  const filteredTickets = useMemo(() => {
    let filtered = allTickets;
    if (myTasks && myUserId) {
      filtered = allTickets.filter(
        (ticket) =>
          Array.isArray(ticket.ticket_status?.assignees) &&
          ticket.ticket_status.assignees.includes(myUserId),
      );
    }
    const seen = new Set();
    return filtered.filter((ticket) => {
      if (seen.has(ticket.ticket_id)) return false;
      seen.add(ticket.ticket_id);
      return true;
    });
  }, [allTickets, myTasks, myUserId]);

  const rows = useMemo(() => {
    return filteredTickets.map((ticket) => {
      const pteam = pteamMap.get(ticket.pteam_id);
      const service = serviceMap.get(ticket.pteam_id + ":" + ticket.service_id);

      return {
        ticket_id: ticket.ticket_id,
        vuln_id: ticket.vuln_id || "-",
        cve_id: "-",
        team: pteam?.pteam_name || "-",
        service: service?.service_name || "-",
        dueDate: ticket.ticket_status?.scheduled_at
          ? new Date(ticket.ticket_status.scheduled_at).toLocaleString(undefined, {
              year: "numeric",
              month: "2-digit",
              day: "2-digit",
              hour: "2-digit",
              minute: "2-digit",
              hour12: false,
            })
          : "-",
        assignee: ticket.ticket_status?.assignees?.length
          ? ticket.ticket_status.assignees.map((userid) => userMap.get(userid) || userid).join(", ")
          : "-",
        ssvc: ticket.ssvc_deployer_priority,
        package_id: "-",
        pteam_id: ticket.pteam_id,
        dependency_id: ticket.dependency_id,
        pteam,
      };
    });
  }, [filteredTickets, pteamMap, userMap, serviceMap]);

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const visibleRows = useMemo(
    () =>
      rows
        .slice()
        .sort(getComparator(order, orderBy))
        .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [rows, order, orderBy, page, rowsPerPage],
  );

  useEffect(() => {
    localStorage.setItem("todoTableOrder", order);
  }, [order]);

  useEffect(() => {
    localStorage.setItem("todoTableOrderBy", orderBy);
  }, [orderBy]);

  return (
    <Paper sx={{ width: "100%" }} variant="outlined">
      {loading ? (
        <Box sx={{ p: 4, textAlign: "center" }}>Loading...</Box>
      ) : (
        <>
          <TableContainer>
            <Table size="small">
              <EnhancedTableHead
                order={order}
                orderBy={orderBy}
                onRequestSort={handleRequestSort}
              />
              <TableBody>
                {visibleRows.map((row, idx) => {
                  let ssvcBgcolor;
                  switch (row.ssvc) {
                    case "immediate":
                      ssvcBgcolor = red[600];
                      break;
                    case "out-of-cycle":
                      ssvcBgcolor = orange[600];
                      break;
                    case "scheduled":
                      ssvcBgcolor = amber[600];
                      break;
                    case "defer":
                      ssvcBgcolor = grey[600];
                      break;
                  }
                  return (
                    <ToDoTableRow
                      key={`${row.ticket_id}-${idx}`}
                      row={row}
                      bgcolor={ssvcBgcolor}
                      ssvc={row.ssvc}
                      vuln_id={row.vuln_id}
                      serviceMap={serviceMap}
                    />
                  );
                })}
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
        </>
      )}
    </Paper>
  );
}

ToDoTable.propTypes = {
  myTasks: PropTypes.bool.isRequired,
  pteamIds: PropTypes.arrayOf(PropTypes.string).isRequired,
};
