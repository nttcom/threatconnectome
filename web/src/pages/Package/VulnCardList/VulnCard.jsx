import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Box, Typography, Button, Divider, Card, CardContent } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useGetPteamTicketsQuery,
  useGetVulnQuery,
  useGetDependenciesQuery,
} from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { sortedSSVCPriorities } from "../../../utils/ssvcUtils";
import { errorToString } from "../../../utils/func";
import { findMatchedVulnPackage } from "../../../utils/vulnUtils";
import { VulnerabilityDrawer } from "../../Vulnerability/VulnerabilityDrawer.jsx";
import { SSVCPriorityCountChip } from "../SSVCPriorityCountChip";

export function VulnCard({ pteamId, serviceId, packageId, vulnId, references }) {
  const skipByAuth = useSkipUntilAuthUserIsReady();
  const skipByPTeamId = pteamId === undefined;
  const skipByServiceId = serviceId === undefined;
  const skipByVulnId = vulnId === undefined;
  const skipBypackageId = packageId === undefined;

  const {
    data: vuln,
    error: vulnError,
    isLoading: vulnIsLoading,
  } = useGetVulnQuery({ path: { vuln_id: vulnId } }, { skip: skipByAuth || skipByVulnId });

  const {
    data: tickets,
    error: ticketsError,
    isLoading: ticketsIsLoading,
  } = useGetPteamTicketsQuery(
    {
      path: { pteam_id: pteamId },
      query: { service_id: serviceId, vuln_id: vulnId, package_id: packageId },
    },
    { skip: skipByAuth || skipByPTeamId || skipByServiceId || skipByVulnId || skipBypackageId },
  );

  const offset = 0;
  const limit = 1000;
  const {
    data: serviceDependencies,
    error: serviceDependenciesError,
    isLoading: serviceDependenciesIsLoading,
  } = useGetDependenciesQuery(
    {
      path: {
        pteam_id: pteamId,
      },
      query: {
        service_id: serviceId,
        package_id: packageId,
        offset: offset,
        limit: limit,
      },
    },
    { skip: skipByAuth || skipByPTeamId || skipByServiceId },
  );

  const [drawerOpen, setDrawerOpen] = useState(false);

  if (skipByAuth || skipByPTeamId || skipByServiceId || skipByVulnId || skipBypackageId)
    return null;
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnIsLoading) return <>Loading Vulnerability...</>;
  if (ticketsError) throw new APIError(errorToString(ticketsError), { api: "getPteamTickets" });
  if (ticketsIsLoading) return <>Loading Tickets...</>;
  if (serviceDependenciesError)
    throw new APIError(errorToString(serviceDependenciesError), { api: "getDependencies" });
  if (serviceDependenciesIsLoading) return <>Loading Dependencies...</>;

  const currentPackage = {
    package_name: serviceDependencies[0]?.package_name,
    package_source_name: serviceDependencies[0]?.package_source_name,
    vuln_matching_ecosystem: serviceDependencies[0]?.vuln_matching_ecosystem,
  };

  const vulnerable_package = findMatchedVulnPackage(vuln.vulnerable_packages, currentPackage);
  const affectedVersions = vulnerable_package?.affected_versions ?? [];
  const patchedVersions = vulnerable_package?.fixed_versions ?? [];

  const ssvcCounts = {};
  sortedSSVCPriorities.forEach((priority) => {
    ssvcCounts[priority] = tickets.filter((t) => t.ssvc_deployer_priority === priority).length;
  });

  return (
    <Card variant="outlined" key={vulnId}>
      <CardContent sx={{ p: 2 }}>
        <Box display="flex" alignItems="center" mb={1}>
          {sortedSSVCPriorities.map((priority) =>
            ssvcCounts[priority] > 0 ? (
              <SSVCPriorityCountChip
                key={priority}
                ssvcPriority={priority}
                count={ssvcCounts[priority]}
                outerSx={{ mr: "6px" }}
              />
            ) : null,
          )}
        </Box>
        <Box display="flex" alignItems="center">
          <Typography variant="h6" gutterBottom sx={{ wordBreak: "break-all" }}>
            {vuln.title}
          </Typography>
        </Box>
        <Typography variant="body2" gutterBottom color="text.secondary">
          Ticket qty: {tickets.length}
        </Typography>
        <Typography variant="body2" gutterBottom color="text.secondary">
          Affected version:
          {affectedVersions.length > 0
            ? affectedVersions.map((ver, i) => (
                <span key={ver}>
                  {ver}
                  {i + 1 !== affectedVersions.length && <br />}
                </span>
              ))
            : "-"}
        </Typography>
        <Typography variant="body2" gutterBottom color="text.secondary">
          Patched version:
          {patchedVersions.length > 0
            ? patchedVersions.map((ver, i) => (
                <span key={ver}>
                  {ver}
                  {i + 1 !== patchedVersions.length && <br />}
                </span>
              ))
            : "-"}
        </Typography>
        <Divider sx={{ my: 1 }} />
        <Box mt={1} sx={{ textAlign: "right" }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<KeyboardDoubleArrowLeftIcon />}
            onClick={() => setDrawerOpen(true)}
          >
            Details
          </Button>
        </Box>
        <VulnerabilityDrawer
          open={drawerOpen}
          setOpen={setDrawerOpen}
          pteamId={pteamId}
          serviceId={serviceId}
          servicePackageId={packageId}
          vulnId={vulnId}
          currentPackage={currentPackage}
          tickets={tickets}
          references={references}
        />
      </CardContent>
    </Card>
  );
}
VulnCard.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  references: PropTypes.array.isRequired,
};
