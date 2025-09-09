import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Button, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import PropTypes from "prop-types";
import { useState, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { ResponsiveDrawer } from "../../../components/ResponsiveDrawer";
import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useGetDependencyQuery,
  useGetPTeamMembersQuery,
  useGetPTeamQuery,
  useGetPTeamServicesQuery,
  useGetVulnQuery,
} from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";
import { preserveParams } from "../../../utils/urlUtils";
import { TicketDetailView } from "../TicketDetailView";

export function ToDoTableRow(props) {
  const { row, ssvcPriority } = props;
  const Icon = ssvcPriority.icon;
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const skip = useSkipUntilAuthUserIsReady();

  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(row.pteam_id, { skip });

  const {
    data: pteamServices,
    error: pteamServicesError,
    isLoading: pteamServicesIsLoading,
  } = useGetPTeamServicesQuery(row.pteam_id, { skip });

  const { data: pteamMembers, error: pteamMembersError } = useGetPTeamMembersQuery(row.pteam_id, {
    skip,
  });

  const {
    data: vuln,
    error: vulnError,
    isLoading: vulnIsLoading,
  } = useGetVulnQuery(row.vuln_id, { skip: !row.vuln_id || row.vuln_id === "-" });

  const {
    data: serviceDependency,
    error: serviceDependencyError,
    isLoading: serviceDependencyIsLoading,
  } = useGetDependencyQuery({ pteamId: row.pteam_id, dependencyId: row.dependency_id }, { skip });

  const assigneeEmails = useMemo(() => {
    if (!row.assignee || row.assignee === "-") return "-";
    const getUserEmail = (userId) => pteamMembers?.[userId]?.email || "";
    const assigneeIds = row.assignee.map((id) => id.trim());
    const emails = assigneeIds.map((userId) => getUserEmail(userId));
    const emailList = emails
      .join(", ")
      .split(",")
      .map((email) => email.trim())
      .filter(Boolean);
    const first = emailList[0];
    const restCount = emailList.length - 1;
    return restCount > 0 ? `${first} +${restCount}` : first;
  }, [row.assignee, pteamMembers]);

  const cveId = vuln?.cve_id || "-";
  const pteamName = pteam?.pteam_name || "-";
  const matchedService = pteamServices?.find?.((service) => service.service_id === row.service_id);
  const serviceName = matchedService?.service_name || "-";
  const packageName = serviceDependency?.package_name || "-";

  const handleRowClick = () => {
    if (!serviceDependency?.package_id) {
      console.warn("Package ID is not available.");
      return;
    }
    const params = preserveParams(location.search);
    params.set("pteamId", row.pteam_id);
    params.set("serviceId", row.service_id);
    const packageId = serviceDependency.package_id;
    navigate(`/packages/${packageId}?` + params.toString());
  };

  if (skip) return <TableRow />;
  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamServicesError)
    throw new APIError(errorToString(pteamServicesError), { api: "getPTeamServices" });
  if (pteamMembersError)
    throw new APIError(errorToString(pteamMembersError), { api: "getPTeamMembers" });
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (serviceDependencyError)
    throw new APIError(errorToString(serviceDependencyError), { api: "getServiceDependencies" });

  return (
    <>
      <TableRow hover sx={{ cursor: "pointer" }} onClick={handleRowClick}>
        <TableCell>{vulnIsLoading ? "..." : cveId}</TableCell>
        <TableCell>{pteamIsLoading ? "..." : pteamName}</TableCell>
        <TableCell>{pteamServicesIsLoading ? "..." : serviceName}</TableCell>
        <TableCell>{serviceDependencyIsLoading ? "..." : packageName}</TableCell>
        <TableCell>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography sx={{ pl: 0.5 }}>{pteamMembers ? assigneeEmails : "..."}</Typography>
          </Box>
        </TableCell>
        <TableCell
          sx={{
            bgcolor: ssvcPriority.style.bgcolor,
            color: "white",
            padding: 0,
          }}
        >
          <Button
            component="div"
            startIcon={<Icon />}
            sx={{ color: "white", justifyContent: "center" }}
          >
            {ssvcPriority.displayName.toUpperCase()}
          </Button>
        </TableCell>
        <TableCell align="right">
          <Button
            variant="outlined"
            startIcon={<KeyboardDoubleArrowLeftIcon />}
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setOpen(true);
            }}
          >
            Details
          </Button>
        </TableCell>
      </TableRow>

      <ResponsiveDrawer
        open={open}
        onClose={() => setOpen(false)}
        title={`Ticket #${row.ticket_id || ""}`}
      >
        <TicketDetailView ticket={row} />
      </ResponsiveDrawer>
    </>
  );
}

ToDoTableRow.propTypes = {
  row: PropTypes.object.isRequired,
  ssvcPriority: PropTypes.shape({
    icon: PropTypes.elementType.isRequired,
    displayName: PropTypes.string.isRequired,
    style: PropTypes.object.isRequired,
  }).isRequired,
};
