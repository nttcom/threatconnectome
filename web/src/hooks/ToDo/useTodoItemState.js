import { useMemo } from "react";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import {
  useGetDependencyQuery,
  useGetPTeamMembersQuery,
  useGetPTeamQuery,
  useGetPTeamServicesQuery,
  useGetVulnQuery,
} from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString, utcStringToLocalDate } from "../../utils/func";

export const useTodoItemState = (ticket) => {
  const skip = useSkipUntilAuthUserIsReady();

  const {
    data: pteam,
    isLoading: pteamIsLoading,
    error: pteamError,
  } = useGetPTeamQuery(
    { path: { pteam_id: ticket.pteam_id } },
    {
      skip: skip || !ticket.pteam_id,
    },
  );

  const {
    data: pteamServices,
    isLoading: pteamServicesIsLoading,
    error: pteamServicesError,
  } = useGetPTeamServicesQuery(
    { path: { pteam_id: ticket.pteam_id } },
    {
      skip: skip || !ticket.pteam_id,
    },
  );

  const service = useMemo(
    () => pteamServices?.find((s) => s.service_id === ticket.service_id),
    [pteamServices, ticket.service_id],
  );

  const { data: pteamMembers, error: pteamMembersError } = useGetPTeamMembersQuery(
    { path: { pteam_id: ticket.pteam_id } },
    {
      skip: skip || !ticket.pteam_id,
    },
  );

  const {
    data: vuln,
    isLoading: vulnIsLoading,
    error: vulnError,
  } = useGetVulnQuery(ticket.vuln_id, {
    skip: skip || !ticket.vuln_id,
  });

  const {
    data: serviceDependency,
    isLoading: serviceDependencyIsLoading,
    error: serviceDependencyError,
  } = useGetDependencyQuery(
    { path: { pteam_id: ticket.pteam_id, dependency_id: ticket.dependency_id } },
    { skip: skip || !ticket.pteam_id || !ticket.dependency_id },
  );

  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamServicesError)
    throw new APIError(errorToString(pteamServicesError), { api: "getPTeamServices" });
  if (pteamMembersError)
    throw new APIError(errorToString(pteamMembersError), { api: "getPTeamMembers" });
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (serviceDependencyError)
    throw new APIError(errorToString(serviceDependencyError), { api: "getServiceDependency" });

  const dueDate = useMemo(() => {
    if (!ticket.ticket_status?.scheduled_at) return "-";
    const formattedDate = utcStringToLocalDate(ticket.ticket_status.scheduled_at, false);
    return formattedDate || "-";
  }, [ticket.ticket_status?.scheduled_at]);

  const displayAssignee = useMemo(() => {
    if (!pteamMembers) return "...";

    const assigneeData = ticket.ticket_status?.assignees;
    if (!assigneeData || assigneeData.length === 0) return "-";

    const getUserEmail = (userId) => pteamMembers?.[userId]?.email || "";
    const assigneeIds = assigneeData.map((id) => id.trim());
    const emails = assigneeIds.map((userId) => getUserEmail(userId));

    const emailList = emails
      .join(", ")
      .split(",")
      .map((email) => email.trim())
      .filter(Boolean);

    if (emailList.length === 0) return "-";

    const first = emailList[0];
    const restCount = emailList.length - 1;
    return restCount > 0 ? `${first} +${restCount}` : first;
  }, [ticket.ticket_status, pteamMembers]);

  return {
    ticket,
    pteam,
    pteamIsLoading,
    service,
    serviceIsLoading: pteamServicesIsLoading,
    pteamMembers,
    vuln,
    vulnIsLoading,
    serviceDependency,
    serviceDependencyIsLoading,
    displayAssignee,
    dueDate,
    ssvc: ticket.ssvc_deployer_priority,
  };
};
