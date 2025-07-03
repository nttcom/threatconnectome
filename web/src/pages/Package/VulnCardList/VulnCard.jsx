import { Box, Typography, Chip, Button, Divider } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useGetPTeamMembersQuery,
  useGetVulnActionsQuery,
  useGetTicketsQuery,
  useGetVulnQuery,
  useGetDependenciesQuery,
} from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { ssvcPriorityProps } from "../../../utils/const";
import { errorToString, searchWorstSSVC } from "../../../utils/func";
import { findMatchedVulnPackage, createActionByFixedVersions } from "../../../utils/vulnUtils";
import { VulnerabilityDrawer } from "../../Vulnerability/VulnerabilityDrawer.jsx";

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
  } = useGetVulnQuery(vulnId, { skip: skipByAuth || skipByVulnId });

  const {
    data: tickets,
    error: ticketsError,
    isLoading: ticketsIsLoading,
  } = useGetTicketsQuery(
    { pteamId, serviceId, vulnId, packageId },
    { skip: skipByAuth || skipByPTeamId || skipByServiceId || skipByVulnId || skipBypackageId },
  );

  // 依存パッケージ情報取得
  const offset = 0;
  const limit = 10000;
  const {
    data: serviceDependencies,
    error: serviceDependenciesError,
    isLoading: serviceDependenciesIsLoading,
  } = useGetDependenciesQuery(
    { pteamId, serviceId, offset, limit },
    { skip: skipByAuth || skipByPTeamId || skipByServiceId },
  );

  // Drawer用
  const [drawerOpen, setDrawerOpen] = useState(false);

  if (skipByAuth || skipByPTeamId || skipByServiceId || skipByVulnId || skipBypackageId)
    return null;
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnIsLoading) return <>Loading Vulnerability...</>;
  if (ticketsError) throw new APIError(errorToString(ticketsError), { api: "getTickets" });
  if (ticketsIsLoading) return <>Loading Tickets...</>;
  if (serviceDependenciesError)
    throw new APIError(errorToString(serviceDependenciesError), { api: "getDependencies" });
  if (serviceDependenciesIsLoading) return <>Loading Dependencies...</>;

  // パッケージ情報
  const currentPackageDependencies = (serviceDependencies ?? []).filter(
    (dependency) => dependency.package_id === packageId,
  );
  const currentPackage = {
    package_name: currentPackageDependencies[0]?.package_name,
    package_source_name: currentPackageDependencies[0]?.package_source_name,
    ecosystem: currentPackageDependencies[0]?.package_ecosystem,
  };

  // 脆弱性パッケージ情報
  const vulnerable_package = findMatchedVulnPackage(vuln.vulnerable_packages, currentPackage);
  const affectedVersions = vulnerable_package?.affected_versions ?? [];
  const patchedVersions = vulnerable_package?.fixed_versions ?? [];

  // SSVC優先度
  const worstPriority = searchWorstSSVC(tickets);
  const priorityColor = ssvcPriorityProps[worstPriority]?.style.bgcolor ?? "grey.300";

  return (
    <Box>
      <Box display="flex" alignItems="center" mb={1}>
        <Box
          sx={{
            width: 8,
            height: 48,
            bgcolor: priorityColor,
            borderRadius: 1,
            mr: 2,
          }}
        />
        <Typography variant="h6" gutterBottom>
          {vuln.title}
        </Typography>
      </Box>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        最終更新: {vuln.updated_at}
      </Typography>
      <Typography variant="body2" gutterBottom>
        チケット数: <Chip label={tickets.length} size="small" color="primary" />
      </Typography>
      <Typography variant="body2" gutterBottom>
        影響バージョン:
        <br />
        {affectedVersions.length > 0
          ? affectedVersions.map((ver, i) => (
              <span key={ver}>
                {ver}
                {i + 1 !== affectedVersions.length && <br />}
              </span>
            ))
          : "-"}
      </Typography>
      <Typography variant="body2" gutterBottom>
        修正バージョン:
        <br />
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
      <Box mt={1}>
        <Button variant="outlined" size="small" onClick={() => setDrawerOpen(true)}>
          詳細を見る
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
      />
    </Box>
  );
}
VulnCard.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  references: PropTypes.array.isRequired,
};
