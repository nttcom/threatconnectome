import { Box, TableCell, TableRow, Tooltip } from "@mui/material";
import PropTypes from "prop-types";

import { SSVCPriorityStatusChip } from "../../../components/SSVCPriorityStatusChip.jsx";
import { utcStringToLocalDate } from "../../../utils/func.js";
import { WarningTooltip } from "../WarningTooltip.jsx";

import { AssigneesSelector } from "./AssigneesSelector.jsx";
import { SafetyImpactSelector } from "./SafetyImpactSelector.jsx";
import { TicketHandlingStatusSelector } from "./TicketHandlingStatusSelector.jsx";

export function TicketTableRow(props) {
  const { pteamId, serviceId, packageId, vulnId, members, references, updateAction, ticket } =
    props;

  const matchedReference = references.find(
    (reference) => reference.dependencyId === ticket.dependency_id,
  );

  const target = matchedReference?.target || "";
  const packageManager = matchedReference?.package_manager || "";

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
      <TableCell
        align="center"
        sx={{
          whiteSpace: "normal",
          wordBreak: "break-all",
        }}
      >
        {packageManager || "-"}
      </TableCell>
      <TableCell>
        <SafetyImpactSelector pteamId={pteamId} ticket={ticket} />
      </TableCell>
      <TableCell>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <TicketHandlingStatusSelector
            pteamId={pteamId}
            serviceId={serviceId}
            vulnId={vulnId}
            packageId={packageId}
            ticketId={ticket.ticket_id}
            currentStatus={ticket.ticket_status}
            updateAction={updateAction}
          />
          {(ticket.ticket_status.ticket_handling_status ?? "alerted") === "alerted" && (
            <WarningTooltip message="No one has acknowledged this vuln" />
          )}
        </Box>
      </TableCell>
      <TableCell>{utcStringToLocalDate(ticket.ticket_status.scheduled_at, false) || "-"}</TableCell>
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
  members: PropTypes.array.isRequired,
  references: PropTypes.array.isRequired,
  updateAction: PropTypes.object.isRequired,
  ticket: PropTypes.object.isRequired,
};
