import { TableCell, TableRow } from "@mui/material";
import PropTypes from "prop-types";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useGetPTeamMembersQuery,
  useGetVulnActionsQuery,
  useGetTicketsQuery,
  useGetVulnQuery,
} from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";

import { TopicTableRowView } from "./TopicTableRowView.jsx";

function SimpleCell(value = "") {
  return (
    <TableRow>
      <TableCell>{value}</TableCell>
    </TableRow>
  );
}

export function TopicTableRow(props) {
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
  } = useGetPTeamMembersQuery(pteamId, { skip: skipByAuth || skipByPTeamId });

  const {
    data: vuln,
    error: vulnError,
    isLoading: vulnIsLoading,
  } = useGetVulnQuery(vulnId, { skip: skipByAuth || skipByVulnId });

  const {
    data: vulnActions,
    error: vulnActionsError,
    isLoading: vulnActionsIsLoading,
  } = useGetVulnActionsQuery(vulnId, { skip: skipByAuth || skipByPTeamId || skipByVulnId });

  const {
    data: tickets,
    error: ticketsRelatedToServiceVulnPackageError,
    isLoading: ticketsRelatedToServiceVulnPackageIsLoading,
  } = useGetTicketsQuery(
    { pteamId, serviceId, vulnId, packageId },
    { skip: skipByAuth || skipByPTeamId || skipByServiceId || skipByVulnId || skipBypackageId },
  );

  if (skipByAuth || skipByPTeamId || skipByServiceId || skipByVulnId || skipBypackageId)
    return SimpleCell("");
  if (membersError) throw new APIError(errorToString(membersError), { api: "getPTeamMembers" });
  if (membersIsLoading) return SimpleCell("Now loading PTeamMembers...");
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnIsLoading) return SimpleCell("Now loading Topic...");
  if (vulnActionsError)
    throw new APIError(errorToString(vulnActionsError), { api: "getPTeamTopicActions" });
  if (vulnActionsIsLoading) return SimpleCell("Now loading topicActions...");
  if (ticketsRelatedToServiceVulnPackageError)
    throw new APIError(errorToString(ticketsRelatedToServiceVulnPackageError), {
      api: "getTicketsRelatedToServiceTopicTag",
    });
  if (ticketsRelatedToServiceVulnPackageIsLoading) return SimpleCell("Now loading tickets...");

  return (
    <TopicTableRowView
      pteamId={pteamId}
      serviceId={serviceId}
      packageId={packageId}
      vulnId={vulnId}
      members={members}
      references={references}
      vuln={vuln}
      vulnActions={vulnActions}
      tickets={tickets}
    />
  );
}
TopicTableRow.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  references: PropTypes.array.isRequired,
};
