import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Button, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import PropTypes from "prop-types";
import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import {
  useGetPTeamQuery,
  useGetPTeamServicesQuery,
  useGetPTeamMembersQuery,
  useGetVulnQuery,
  useGetVulnActionsQuery,
  useGetDependencyQuery,
} from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString , utcStringToLocalDate } from "../../utils/func";

import { ToDoDrawer } from "./ToDoDrawer";

function SimpleCell(value = "") {
  return (
    <TableRow>
      <TableCell>{value}</TableCell>
    </TableRow>
  );
}

export function ToDoTableRow(props) {
  const { row, ssvcPriority, vuln_id } = props;
  const Icon = ssvcPriority.icon;
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const skip = useSkipUntilAuthUserIsReady();
  const skipDependency = !row.dependency_id;

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
  const {
    data: pteamMembers,
    error: pteamMembersError,
    isLoading: pteamMembersIsLoading,
  } = useGetPTeamMembersQuery(row.pteam_id, { skip });
  const {
    data: vuln,
    error: vulnError,
    isLoading: vulnIsLoading,
  } = useGetVulnQuery(vuln_id, { skip });
  const {
    data: vulnActions,
    error: vulnActionsError,
    isLoading: vulnActionsIsLoading,
  } = useGetVulnActionsQuery(vuln_id, { skip });
  const {
    data: serviceDependency,
    error: serviceDependencyError,
    isLoading: serviceDependencyIsLoading,
  } = useGetDependencyQuery(
    { pteamId: row.pteam_id, dependencyId: row.dependency_id },
    { skip: skipDependency },
  );

  const assigneeEmails = useMemo(() => {
    if (!row.assignee || row.assignee === "-") return "-";

    const getUserEmail = (userId) => {
      return pteamMembers?.[userId]?.email || "";
    };

    const assigneeIds = row.assignee.split(",").map((id) => id.trim());
    const emails = assigneeIds.map((userId) => getUserEmail(userId));
    return emails.join(", ");
  }, [row.assignee, pteamMembers]);

  const pteamName = pteam?.pteam_name || "";
  const matchedService = pteamServices?.find?.((service) => service.service_id === row.service_id);
  const serviceName = matchedService?.service_name || "-";

  const handleRowClick = () => {
    if (!serviceDependency) {
      console.warn("Service dependency information is not available.");
      return;
    }
    const packageId = serviceDependency.package_id;
    navigate(`/packages/${packageId}?pteamId=${row.pteam_id}&serviceId=${row.service_id}`);
  };

  if (skip) return SimpleCell("");

  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamServicesError)
    throw new APIError(errorToString(pteamServicesError), { api: "getPTeamServices" });
  if (pteamMembersError)
    throw new APIError(errorToString(pteamMembersError), { api: "getPTeamMembers" });
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnActionsError)
    throw new APIError(errorToString(vulnActionsError), { api: "getVulnActions" });
  if (serviceDependencyError)
    throw new APIError(errorToString(serviceDependencyError), { api: "getServiceDependencies" });

  if (pteamIsLoading) return SimpleCell("Now loading PTeam...");
  if (pteamServicesIsLoading) return SimpleCell("Now loading PTeam Services...");
  if (pteamMembersIsLoading) return SimpleCell("Now loading PTeam Members...");
  if (vulnIsLoading) return SimpleCell("Now loading Vulnerability...");
  if (vulnActionsIsLoading) return SimpleCell("Now loading VulnActions...");
  if (serviceDependencyIsLoading) return SimpleCell("Now loading Service Dependencies...");

  return (
    <>
      <TableRow hover sx={{ cursor: "pointer" }} onClick={handleRowClick}>
        <TableCell>{vuln?.cve_id || "-"}</TableCell>
        <TableCell>{pteamName || "-"}</TableCell>
        <TableCell>{serviceName || "-"}</TableCell>
        <TableCell>
          {(() => {
            if (!row?.dueDate || row.dueDate === "-") return "-";
            return utcStringToLocalDate(row.dueDate);
          })()}
        </TableCell>
        <TableCell>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography sx={{ pl: 0.5 }}>
              {assigneeEmails === "-"
                ? "-"
                : (() => {
                    const emails = assigneeEmails
                      .split(",")
                      .map((email) => email.trim())
                      .filter(Boolean);
                    const first = emails[0];
                    const restCount = emails.length - 1;
                    return restCount > 0 ? `${first} +${restCount}` : first;
                  })()}
            </Typography>
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
            sx={{
              color: "white",
              justifyContent: "center",
            }}
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
      <ToDoDrawer
        open={open}
        setOpen={setOpen}
        row={row}
        pteamName={pteamName}
        serviceName={serviceName}
        pteamMembers={pteamMembers}
        assigneeEmails={assigneeEmails}
        serviceDependency={serviceDependency}
        vuln={vuln}
        vulnActions={vulnActions}
        ssvcPriority={ssvcPriority}
      />
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
  vuln_id: PropTypes.string,
};
