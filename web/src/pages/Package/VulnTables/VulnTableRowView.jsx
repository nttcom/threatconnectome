import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Button, Collapse, IconButton, TableCell, TableRow } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useGetDependenciesQuery } from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { ssvcPriorityProps } from "../../../utils/const.js";
import { errorToString, searchWorstSSVC } from "../../../utils/func";
import { createActionByFixedVersions, findMatchedVulnPackage } from "../../../utils/vulnUtils.js";
import { VulnerabilityDrawer } from "../../Vulnerability/VulnerabilityDrawer.jsx";

import { TicketTable } from "./TicketTable.jsx";
import { TicketTableRow } from "./TicketTableRow.jsx";

export function VulnTableRowView(props) {
  const { pteamId, serviceId, packageId, vulnId, members, references, vuln, vulnActions, tickets } =
    props;
  const [ticketOpen, setTicketOpen] = useState(true);
  const [vulnDrawerOpen, setVulnDrawerOpen] = useState(false);
  const skip = useSkipUntilAuthUserIsReady();
  const getDependenciesReady = !skip && pteamId && serviceId;

  const offset = 0;
  const limit = 10000;
  const {
    data: serviceDependencies,
    error: serviceDependenciesError,
    isLoading: serviceDependenciesIsLoading,
  } = useGetDependenciesQuery(
    { pteamId, serviceId, offset, limit },
    { skip: !getDependenciesReady },
  );

  if (skip) return <></>;
  if (serviceDependenciesError)
    throw new APIError(errorToString(serviceDependenciesError), { api: "getDependencies" });
  if (serviceDependenciesIsLoading) return <>Now loading Service Dependencies...</>;
  const currentPackageDependencies = (serviceDependencies ?? []).filter(
    (dependency) => dependency.package_id === packageId,
  );
  const currentPackage = {
    package_name: currentPackageDependencies[0].package_name,
    package_source_name: currentPackageDependencies[0].package_source_name,
    ecosystem: currentPackageDependencies[0].package_ecosystem,
    vuln_matching_ecosystem: currentPackageDependencies[0].vuln_matching_ecosystem,
  };

  // Get the matched vulnerable package from vulnerable_packages and currentPackage
  const vulnerable_package = findMatchedVulnPackage(vuln.vulnerable_packages, currentPackage);
  const affectedVersions = vulnerable_package.affected_versions;
  const patchedVersions = vulnerable_package.fixed_versions;
  const actionByFixedVersions = createActionByFixedVersions(
    affectedVersions,
    patchedVersions,
    vulnerable_package.affected_name,
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
                  actionByFixedVersions={actionByFixedVersions}
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
        currentPackage={currentPackage}
        tickets={tickets}
        references={references}
      />
    </>
  );
}
VulnTableRowView.propTypes = {
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
