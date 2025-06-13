import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Button, Chip, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { ToDoDrawer } from "./ToDoDrawer";

export function ToDoTableRow(props) {
  const { row, bgcolor, ssvc } = props;
  const [open, setOpen] = useState(false);
  return (
    <>
      <TableRow key={row}>
        <TableCell>{row.cve}</TableCell>
        <TableCell>{row.team}</TableCell>
        <TableCell>{row.service}</TableCell>
        <TableCell>{row.dueDate}</TableCell>
        <TableCell>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Chip label={row.assignee} />
            <Typography sx={{ pl: 0.5 }}>+1</Typography>
          </Box>
        </TableCell>
        <TableCell
          sx={{
            bgcolor: bgcolor,
            color: "white",
          }}
        >
          {ssvc}
        </TableCell>
        <TableCell align="right">
          <Button
            variant="outlined"
            startIcon={<KeyboardDoubleArrowLeftIcon />}
            size="small"
            onClick={() => setOpen(true)}
          >
            Details
          </Button>
        </TableCell>
      </TableRow>
      <ToDoDrawer open={open} setOpen={setOpen} />
    </>
  );
}

ToDoTableRow.propTypes = {
  row: PropTypes.object.required,
  bgcolor: PropTypes.string.required,
  ssvc: PropTypes.string.required,
};
