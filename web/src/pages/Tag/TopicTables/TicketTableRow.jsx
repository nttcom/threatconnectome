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

import { SSVCPriorityStatusChip } from "../../../components/SSVCPriorityStatusChip.jsx";
import { WarningTooltip } from "../WarningTooltip.jsx";

import { AssigneesSelector } from "./AssigneesSelector";
import { SafetyImpactSelector } from "./SafetyImpactSelector.jsx";
import { TopicStatusSelector } from "./TopicStatusSelector.jsx";

export function TicketTableRow(props) {
  const {
    pteamId,
    serviceId,
    tagId,
    topicId,
    allTags,
    members,
    references,
    topic,
    topicActions,
    ticket,
  } = props;

  const statusList = ["Alerted", "Acknowledged", "Scheduled", "Completed"];
  const [currentStatus, setCurrentStatus] = useState(statusList[0]);
  const target = references.filter(
    (reference) => reference.dependencyId === ticket.threat.dependency_id,
  )[0].target;

  return (
    <TableRow>
      <TableCell>{target}</TableCell>
      <TableCell>
        <SafetyImpactSelector threatId={ticket.threat.threat_id} />
      </TableCell>
      <TableCell>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <TopicStatusSelector
            pteamId={pteamId}
            serviceId={serviceId}
            topicId={topicId}
            tagId={tagId}
            ticketId={ticket.ticket_id}
            currentStatus={ticket.ticket_status}
            topicActions={topicActions}
          />
          {(ticket.ticket_status.topic_status ?? "alerted") === "alerted" && (
            <WarningTooltip message="No one has acknowledged this topic" />
          )}
        </Box>
      </TableCell>
      <TableCell>{ticket.ticket_status.scheduled_at}</TableCell>
      <TableCell>
        <AssigneesSelector
          key={ticket.ticket_status.assignees.join("")}
          pteamId={pteamId}
          serviceId={serviceId}
          topicId={topicId}
          tagId={tagId}
          ticketId={ticket.ticket_id}
          currentAssigneeIds={ticket.ticket_status.assignees}
          members={members}
        />
      </TableCell>
      <TableCell>
        <Box sx={{ display: "flex", justifyContent: "center" }}>
          <SSVCPriorityStatusChip displaySSVCPriority={ticket.ssvc_deployer_priority} />
        </Box>
      </TableCell>
    </TableRow>
  );
}

TicketTableRow.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  tagId: PropTypes.string.isRequired,
  topicId: PropTypes.string.isRequired,
  allTags: PropTypes.array.isRequired,
  members: PropTypes.object.isRequired,
  references: PropTypes.array.isRequired,
  topic: PropTypes.object.isRequired,
  topicActions: PropTypes.array.isRequired,
  ticket: PropTypes.object.isRequired,
};
