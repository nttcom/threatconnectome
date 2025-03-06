import {
  Box,
  Chip,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  TableCell,
  TableRow,
} from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { WarningTooltip } from "../WarningTooltip.jsx";

import { SSVCPriorityStatusChip } from "../../../components/SSVCPriorityStatusChip.jsx";
import { SelectSafetyImpactForm } from "./SelectSafetyImpactForm.jsx";

export function TicketTableRow(props) {
  const { ticket } = props;
  const userNames = ["test@example.com", "test2@example.com"];
  const [assignees, setAssignees] = useState([]);

  const handleChange = (event) => {
    const {
      target: { value },
    } = event;
    setAssignees(value);
  };

  const statusList = ["Alerted", "Acknowledged", "Scheduled", "Completed"];
  const [currentStatus, setCurrentStatus] = useState(statusList[0]);

  const displaySSVCPriority = "immediate";

  return (
    <TableRow>
      <TableCell>{ticket.target}</TableCell>
      <TableCell>
        <SelectSafetyImpactForm />
      </TableCell>
      <TableCell>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <FormControl sx={{ width: 140 }} size="small" variant="standard">
            <Select value={currentStatus} onChange={(e) => setCurrentStatus(e.target.value)}>
              {statusList.map((status) => (
                <MenuItem key={status} value={status}>
                  {status}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {currentStatus === "Alerted" && (
            <WarningTooltip message="No one has acknowledged this topic" />
          )}
        </Box>
      </TableCell>
      <TableCell>{ticket.dueDate}</TableCell>
      <TableCell>
        <FormControl sx={{ width: 200 }} size="small">
          <InputLabel>Assignees</InputLabel>
          <Select
            multiple
            value={assignees}
            onChange={handleChange}
            input={<OutlinedInput label="Assingees" />}
            renderValue={(selected) => (
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip key={value} label={value} size="small" />
                ))}
              </Box>
            )}
          >
            {userNames.map((name) => (
              <MenuItem key={name} value={name}>
                {name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </TableCell>
      <TableCell>
        <Box sx={{ display: "flex", justifyContent: "center" }}>
          <SSVCPriorityStatusChip displaySSVCPriority={displaySSVCPriority} />
        </Box>
      </TableCell>
    </TableRow>
  );
}

TicketTableRow.propTypes = {
  ticket: PropTypes.object,
};
