import { TableCell, TableRow } from "@mui/material";
import PropTypes from "prop-types";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth.js";
import {
  useGetPTeamMembersQuery,
  useGetPteamTicketsQuery,
  useGetVulnQuery,
} from "../../../services/tcApi.js";
import { APIError } from "../../../utils/APIError.js";
import { errorToString } from "../../../utils/func.js";

import { VulnTableRowView } from "./VulnTableRowView.jsx";

function SimpleCell(value = "") {
  return (
    <TableRow>
      <TableCell>{value}</TableCell>
    </TableRow>
  );
}

export function VulnTableRow(props) {
  const { pteamId, serviceId, packageId, vulnId, references } = props;

  const skipByAuth = useSkipUntilAuthUserIsReady();

  const skipByPTeamId = pteamId === undefined;
  const skipByServiceId = serviceId === undefined;
  const skipByVulnId = vulnId === undefined;
  const skipBypackageId = packageId === undefined;

  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetPTeamMembersQuery(
    { path: { pteam_id: pteamId } },
    { skip: skipByAuth || skipByPTeamId },
  );

  const {
    data: vuln,
    error: vulnError,
    isLoading: vulnIsLoading,
  } = useGetVulnQuery({ path: { vuln_id: vulnId } }, { skip: skipByAuth || skipByVulnId });

  const {
    data: tickets,
    error: ticketsRelatedToServiceVulnPackageError,
    isLoading: ticketsRelatedToServiceVulnPackageIsLoading,
  } = useGetPteamTicketsQuery(
    {
      path: { pteam_id: pteamId },
      query: { service_id: serviceId, vuln_id: vulnId, package_id: packageId },
    },
    { skip: skipByAuth || skipByPTeamId || skipByServiceId || skipByVulnId || skipBypackageId },
  );

  if (skipByAuth || skipByPTeamId || skipByServiceId || skipByVulnId || skipBypackageId)
    return SimpleCell("");
  if (membersError) throw new APIError(errorToString(membersError), { api: "getPTeamMembers" });
  if (membersIsLoading) return SimpleCell("Now loading PTeamMembers...");
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnIsLoading) return SimpleCell("Now loading Vuln...");
  if (ticketsRelatedToServiceVulnPackageError)
    throw new APIError(errorToString(ticketsRelatedToServiceVulnPackageError), {
      api: "getPteamTickets",
    });
  if (ticketsRelatedToServiceVulnPackageIsLoading) return SimpleCell("Now loading tickets...");

  return (
    <VulnTableRowView
      pteamId={pteamId}
      serviceId={serviceId}
      packageId={packageId}
      vulnId={vulnId}
      members={members}
      references={references}
      vuln={vuln}
      tickets={tickets}
    />
  );
}
VulnTableRow.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  references: PropTypes.array.isRequired,
};
