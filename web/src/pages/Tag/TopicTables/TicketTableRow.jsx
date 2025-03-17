import { Box, TableCell, TableRow, Tooltip } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { SSVCPriorityStatusChip } from "../../../components/SSVCPriorityStatusChip.jsx";
import { ssvcPriorityProps } from "../../../utils/const";
import { WarningTooltip } from "../WarningTooltip.jsx";

import { AssigneesSelector } from "./AssigneesSelector";
import { SafetyImpactSelector } from "./SafetyImpactSelector.jsx";
import { TopicStatusSelector } from "./TopicStatusSelector.jsx";

export function TicketTableRow(props) {
  const { pteamId, serviceId, tagId, topicId, members, references, topicActions, ticket } = props;

  const target = references.filter(
    (reference) => reference.dependencyId === ticket.threat.dependency_id,
  )[0].target;

  return (
    <TableRow>
      <Tooltip arrow placement="bottom-end" title={target}>
        <TableCell
          sx={{
            maxWidth: 200,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            borderLeft: `solid 5px ${ssvcPriorityProps[ticket.ssvc_deployer_priority].style.bgcolor}`,
          }}
        >
          {target}
        </TableCell>
      </Tooltip>
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
  members: PropTypes.object.isRequired,
  references: PropTypes.array.isRequired,
  topicActions: PropTypes.array.isRequired,
  ticket: PropTypes.object.isRequired,
};
