import { Box, TableCell, TableRow, Tooltip } from "@mui/material";
import PropTypes from "prop-types";

import { SSVCPriorityStatusChip } from "../../../components/SSVCPriorityStatusChip.jsx";
import { WarningTooltip } from "../WarningTooltip.jsx";

import { AssigneesSelector } from "./AssigneesSelector.jsx";
import { SafetyImpactSelector } from "./SafetyImpactSelector.jsx";
import { VulnStatusSelector } from "./VulnStatusSelector.jsx";

export function TicketTableRow(props) {
  const {
    pteamId,
    serviceId,
    packageId,
    vulnId,
    members,
    references,
    actionText,
    vulnActions,
    ticket,
  } = props;

  const target = references.filter(
    (reference) => reference.dependencyId === ticket.dependency_id,
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
          }}
        >
          {target}
        </TableCell>
      </Tooltip>
      <TableCell>
        <SafetyImpactSelector pteamId={pteamId} ticket={ticket} />
      </TableCell>
      <TableCell>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <VulnStatusSelector
            pteamId={pteamId}
            serviceId={serviceId}
            vulnId={vulnId}
            packageId={packageId}
            ticketId={ticket.ticket_id}
            currentStatus={ticket.ticket_status}
            actionText={actionText}
            vulnActions={vulnActions}
          />
          {(ticket.ticket_status.vuln_status ?? "alerted") === "alerted" && (
            <WarningTooltip message="No one has acknowledged this vuln" />
          )}
        </Box>
      </TableCell>
      <TableCell>{ticket.ticket_status.scheduled_at}</TableCell>
      <TableCell>
        <AssigneesSelector
          key={ticket.ticket_status.assignees.join("")}
          pteamId={pteamId}
          serviceId={serviceId}
          vulnId={vulnId}
          packageId={packageId}
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
  packageId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  members: PropTypes.object.isRequired,
  references: PropTypes.array.isRequired,
  actionText: PropTypes.object.isRequired,
  vulnActions: PropTypes.array.isRequired,
  ticket: PropTypes.object.isRequired,
};
