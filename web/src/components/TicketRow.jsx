import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
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
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import { tooltipClasses } from "@mui/material/Tooltip";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { WarningTooltip } from "../pages/Tag/WarningTooltip.jsx";
import { safetyImpactProps, sortedSafetyImpacts } from "../utils/const.js";

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
          <StyledTooltip
            arrow
            title={
              <>
                <Typography variant="body2">
                  The safety impact of the vulnerability. (based on IEC 61508)
                </Typography>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "center",
                    p: 1,
                  }}
                >
                  <ToggleButtonGroup
                    color="primary"
                    size="small"
                    orientation="vertical"
                    value={currentSafetyImpact}
                  >
                    {sortedSafetyImpacts.map((safetyImpact) => {
                      const displayName = safetyImpactProps[safetyImpact].displayName;
                      return (
                        <ToggleButton key={safetyImpact} value={displayName} disabled>
                          {displayName}
                        </ToggleButton>
                      );
                    })}
                  </ToggleButtonGroup>
                </Box>
              </>
            }
          >
            <HelpOutlineOutlinedIcon color="action" fontSize="small" />
          </StyledTooltip>
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
