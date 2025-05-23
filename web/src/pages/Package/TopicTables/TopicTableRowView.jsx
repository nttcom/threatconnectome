import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Button, Collapse, IconButton, TableCell, TableRow } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { ssvcPriorityProps } from "../../../utils/const.js";
import { createActionText, searchWorstSSVC } from "../../../utils/func.js";
import { VulnerabilityDrawer } from "../../Vulnerability/VulnerabilityDrawer.jsx";

import { TicketTable } from "./TicketTable.jsx";
import { TicketTableRow } from "./TicketTableRow.jsx";

export function TopicTableRowView(props) {
  const { pteamId, serviceId, packageId, vulnId, members, references, vuln, vulnActions, tickets } =
    props;
  const [ticketOpen, setTicketOpen] = useState(true);
  const [vulnDrawerOpen, setVulnDrawerOpen] = useState(false);

  const vulnerable_package = vuln.vulnerable_packages.find(
    (vulnerable_package) => vulnerable_package.package_id === packageId,
  );
  const affectedVersions = vulnerable_package.affected_versions;
  const patchedVersions = vulnerable_package.fixed_versions;
  const actionText = createActionText(
    affectedVersions.join(),
    patchedVersions.join(),
    vulnerable_package.name,
  );

  return (
    <>
      <TableRow>
        <TableCell
          sx={{
            bgcolor: "grey.50",
            borderLeft: `solid 5px ${ssvcPriorityProps[searchWorstSSVC(tickets)].style.bgcolor}`,
          }}
        >
          <IconButton size="small" onClick={() => setTicketOpen(!ticketOpen)}>
            {ticketOpen ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell sx={{ maxWidth: 300, bgcolor: "grey.50" }}>{vuln.title}</TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {tickets.length}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {vuln.updated_at}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {affectedVersions.map((affectedVersion, index) =>
            index + 1 === affectedVersions.length ? (
              affectedVersion
            ) : (
              <>
                {affectedVersion}
                <br />
              </>
            ),
          )}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {patchedVersions.map((patchedVersion, index) =>
            index + 1 === patchedVersions.length ? (
              patchedVersion
            ) : (
              <>
                {patchedVersion}
                <br />
              </>
            ),
          )}
        </TableCell>
        <TableCell align="right" sx={{ bgcolor: "grey.50" }}>
          <Button
            variant="outlined"
            startIcon={<KeyboardDoubleArrowLeftIcon />}
            size="small"
            onClick={() => setVulnDrawerOpen(true)}
          >
            Details
          </Button>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell
          sx={{
            borderLeft: `solid 5px ${ssvcPriorityProps[searchWorstSSVC(tickets)].style.bgcolor}`,
            py: 0,
          }}
          colSpan={7}
        >
          <Collapse in={ticketOpen} timeout="auto" unmountOnExit>
            <TicketTable>
              {tickets.map((ticket) => (
                <TicketTableRow
                  key={ticket.ticket_id}
                  pteamId={pteamId}
                  serviceId={serviceId}
                  packageId={packageId}
                  vulnId={vulnId}
                  members={members}
                  references={references}
                  actionText={actionText}
                  vulnActions={vulnActions}
                  ticket={ticket}
                />
              ))}
            </TicketTable>
          </Collapse>
        </TableCell>
      </TableRow>
      <VulnerabilityDrawer
        open={vulnDrawerOpen}
        setOpen={setVulnDrawerOpen}
        pteamId={pteamId}
        serviceId={serviceId}
        servicePackageId={packageId}
        vulnId={vulnId}
      />
    </>
  );
}
TopicTableRowView.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  members: PropTypes.object.isRequired,
  references: PropTypes.array.isRequired,
  vuln: PropTypes.object.isRequired,
  vulnActions: PropTypes.array.isRequired,
  tickets: PropTypes.array.isRequired,
};
