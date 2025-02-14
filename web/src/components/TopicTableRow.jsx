import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Button, Collapse, IconButton, TableCell, TableRow } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { TicketTable } from "./TicketTable.jsx";
import { TopicDetailsDrawer } from "./TopicDetailsDrawer";

export function TopicTableRow(props) {
  const { row } = props;
  const [open, setOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <>
      <TableRow>
        <TableCell sx={{ bgcolor: "grey.50" }}>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell sx={{ maxWidth: 300, bgcolor: "grey.50" }}>{row.title}</TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {row.tickets.length}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {row.lastUpdated}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {"'<1.26.19',"}
          <br />
          {"'>=2.0.0, <2.2.2'"}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {"'1.26.19',"}
          <br />
          {"'2.2.2'"}
        </TableCell>
        <TableCell align="right" sx={{ bgcolor: "grey.50" }}>
          <Button
            variant="outlined"
            startIcon={<KeyboardDoubleArrowLeftIcon />}
            size="small"
            sx={{ ml: 1 }}
            onClick={() => setDrawerOpen(true)}
          >
            Details
          </Button>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell sx={{ py: 0 }} colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <TicketTable tickets={row.tickets} />
          </Collapse>
        </TableCell>
      </TableRow>
      <TopicDetailsDrawer open={drawerOpen} setOpen={setDrawerOpen} />
    </>
  );
}

TopicTableRow.propTypes = {
  row: PropTypes.shape({
    title: PropTypes.string.isRequired,
    tickets: PropTypes.array,
    lastUpdated: PropTypes.string,
  }).isRequired,
  index: PropTypes.number,
};
