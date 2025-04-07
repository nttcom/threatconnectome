import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TablePagination from "@mui/material/TablePagination";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import { amber, grey, orange, red } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState, useMemo } from "react";

import { ToDoTableRow } from "./ToDoTableRow";

function createData(cve, team, service, dueDate, assignee, ssvc) {
  return {
    cve,
    team,
    service,
    dueDate,
    assignee,
    ssvc,
  };
}

const rows = [
  createData("CVE-XXXX-XXXX", "team_name", "service_name", "2024/12/12 10:00", "test_user1", 0),
  createData("CVE-XXXX-XXXX", "team_name", "service_name", "2024/12/12 10:00", "test_user2", 1),
  createData("CVE-XXXX-XXXX", "team_name", "service_name", "2024/12/12 10:00", "test_user3", 2),
  createData("CVE-XXXX-XXXX", "team_name", "service_name", "2024/12/12 10:00", "test_user4", 0),
  createData("CVE-XXXX-XXXX", "team_name", "service_name", "2024/12/12 10:00", "test_user5", 3),
];

function EnhancedTableHead(props) {
  const { order, orderBy, onRequestSort } = props;
  const createSortHandler = (property) => (event) => {
    onRequestSort(event, property);
  };

  const headCells = [
    {
      id: "cve",
      label: "CVE-ID",
    },
    {
      id: "team",
      label: "Team",
    },
    {
      id: "service",
      label: "Service",
    },
    {
      id: "dueDate",
      label: "Due date",
    },
    {
      id: "assignee",
      label: "Assignee",
    },
    {
      id: "ssvc",
      label: "SSVC",
    },
  ];

  return (
    <TableHead>
      <TableRow>
        {headCells.map((headCell) => (
          <TableCell key={headCell.id} sortDirection={orderBy === headCell.id ? order : false}>
            <TableSortLabel
              active={orderBy === headCell.id}
              direction={orderBy === headCell.id ? order : "asc"}
              onClick={createSortHandler(headCell.id)}
            >
              {headCell.label}
            </TableSortLabel>
          </TableCell>
        ))}
        <TableCell />
      </TableRow>
    </TableHead>
  );
}

EnhancedTableHead.propTypes = {
  onRequestSort: PropTypes.func.isRequired,
  order: PropTypes.oneOf(["asc", "desc"]).isRequired,
  orderBy: PropTypes.string.isRequired,
};

function descendingComparator(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

function getComparator(order, orderBy) {
  return order === "desc"
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

export function ToDoTable() {
  const [order, setOrder] = useState("asc");
  const [orderBy, setOrderBy] = useState("ssvc");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

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
    [order, orderBy, page, rowsPerPage],
  );

  return (
    <Paper sx={{ width: "100%" }} variant="outlined">
      <TableContainer>
        <Table size="small">
          <EnhancedTableHead order={order} orderBy={orderBy} onRequestSort={handleRequestSort} />
          <TableBody>
            {visibleRows.map((row) => {
              let ssvc;
              switch (row.ssvc) {
                case 0:
                  ssvc = "Immediate";
                  break;
                case 1:
                  ssvc = "Out-of-Cycle";
                  break;
                case 2:
                  ssvc = "Scheduled";
                  break;
                case 3:
                  ssvc = "Defer";
                  break;
              }

              let ssvcBgcolor;
              switch (ssvc) {
                case "Immediate":
                  ssvcBgcolor = red[600];
                  break;
                case "Out-of-Cycle":
                  ssvcBgcolor = orange[600];
                  break;
                case "Scheduled":
                  ssvcBgcolor = amber[600];
                  break;
                case "Defer":
                  ssvcBgcolor = grey[600];
                  break;
              }

              return <ToDoTableRow key={row} row={row} bgcolor={ssvcBgcolor} ssvc={ssvc} />;
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
    </Paper>
  );
}
