import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  Box,
  Chip,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  TableCell,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import { tooltipClasses } from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { WarningTooltip } from "../pages/Tag/WarningTooltip.jsx";

import { SSVCPriorityStatusChip } from "./SSVCPriorityStatusChip.jsx";

export function TicketRow(props) {
  const { ticket } = props;
  const userNames = ["test@example.com", "test2@example.com"];
  const [assignees, setAssignees] = useState([]);

  const handleChange = (event) => {
    const {
      target: { value },
    } = event;
    setAssignees(value);
  };

  const StyledTooltip = styled(({ className, ...props }) => (
    <Tooltip {...props} classes={{ popper: className }} />
  ))(() => ({
    [`& .${tooltipClasses.arrow}`]: {
      "&:before": {
        border: "1px solid #dadde9",
      },
      color: "#f5f5f9",
    },
    [`& .${tooltipClasses.tooltip}`]: {
      backgroundColor: "#f5f5f9",
      color: "rgba(0, 0, 0, 0.87)",
      border: "1px solid #dadde9",
    },
  }));

  const safetyImpactList = ["Negligible", "Marginal", "Critical", "Catastrophic"];
  const [currentSafetyImpact, setCurrentSafetyImpact] = useState(safetyImpactList[0]);
  const defaultSafetyImpact = safetyImpactList[0];

  const statusList = ["Alerted", "Acknowledged", "Scheduled", "Completed"];
  const [currentStatus, setCurrentStatus] = useState(statusList[0]);

  const displaySSVCPriority = "immediate";

  return (
    <TableRow>
      <TableCell>{ticket.target}</TableCell>
      <TableCell>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <FormControl sx={{ width: 130 }} size="small" variant="standard">
            <Select
              value={currentSafetyImpact}
              onChange={(e) => setCurrentSafetyImpact(e.target.value)}
            >
              {safetyImpactList.map((safetyImpact) => (
                <MenuItem key={safetyImpact} value={safetyImpact}>
                  {safetyImpact}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {currentSafetyImpact !== defaultSafetyImpact && (
            <StyledTooltip
              arrow
              title={
                <>
                  <Typography variant="h6">
                    Why was it changed from the default safety impact?
                  </Typography>
                  <Box sx={{ p: 1 }}>
                    <Typography variant="body2">
                      Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
                      incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
                      nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
                      eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt
                      in culpa qui officia deserunt mollit anim id est laborum.
                    </Typography>
                  </Box>
                </>
              }
            >
              <IconButton size="small">
                <InfoOutlinedIcon color="primary" fontSize="small" />
              </IconButton>
            </StyledTooltip>
          )}
        </Box>
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
            input={<OutlinedInput id="select-multiple-chip" label="Assingees" />}
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

TicketRow.propTypes = {
  ticket: PropTypes.object,
};
