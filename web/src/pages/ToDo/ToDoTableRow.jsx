import { useNavigate } from "react-router-dom";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Button, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import PropTypes from "prop-types";
import { useState } from "react";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import {
  useGetVulnQuery,
  useGetVulnActionsQuery,
  useGetDependencyQuery,
} from "../../services/tcApi";
import { ToDoDrawer } from "./ToDoDrawer";

function SimpleCell(value = "") {
  return (
    <TableRow>
      <TableCell>{value}</TableCell>
    </TableRow>
  );
}

export function ToDoTableRow(props) {
  const { row, bgcolor, ssvc, vuln_id, serviceMap } = props;
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const skip = useSkipUntilAuthUserIsReady();

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
    data: dependency,
    error: dependencyError,
    isLoading: dependencyIsLoading,
  } = useGetDependencyQuery(
    row.dependency_id ? { pteamId: row.pteam_id, dependencyId: row.dependency_id } : skipToken,
  );

  if (skip) return SimpleCell("");
  if (vulnError) throw new APIError(errorToString(vulnError), { api: "getVuln" });
  if (vulnActionsError)
    throw new APIError(errorToString(vulnActionsError), { api: "getVulnActions" });
  if (dependencyError) throw new APIError(errorToString(dependencyError), { api: "getDependency" });
  if (vulnIsLoading) return SimpleCell("Now loading Vulnerability...");
  if (vulnActionsIsLoading) return SimpleCell("Now loading VulnActions...");
  if (dependencyIsLoading) return SimpleCell("Now loading Dependency...");

  const servicePteamId = row.pteam_id;
  const serviceId = dependency?.service_id ?? row.service_id;
  const service = serviceMap.get(servicePteamId + ":" + serviceId);

  const handleRowClick = () => {
    const packageId = dependency.package_id;
    const pteamId = row.pteam_id;
    const serviceId = dependency.service_id || row.pteam?.services?.[0]?.service_id;
    navigate(`/packages/${packageId}?pteamId=${pteamId}&serviceId=${serviceId}`);
  };

  return (
    <>
      <TableRow hover sx={{ cursor: "pointer" }} onClick={handleRowClick}>
        <TableCell>{vuln?.cve_id || "-"}</TableCell>
        <TableCell>{row.team}</TableCell>
        <TableCell>{service?.service_name || "-"}</TableCell>
        <TableCell>{row.dueDate}</TableCell>
        <TableCell>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography sx={{ pl: 0.5 }}>
              {row.assignee === "-"
                ? "-"
                : (() => {
                    const assignees = row.assignee.split(",").filter(Boolean);
                    const first = assignees[0];
                    const restCount = assignees.length - 1;
                    return restCount > 0 ? `${first} +${restCount}` : first;
                  })()}
            </Typography>
          </Box>
        </TableCell>
        <TableCell
          sx={{
            bgcolor: bgcolor,
            color: "white",
          }}
        >
          {ssvc}
        </TableCell>
        <TableCell align="right">
          <Button
            variant="outlined"
            startIcon={<KeyboardDoubleArrowLeftIcon />}
            size="small"
            onClick={() => setOpen(true)}
          >
            Details
          </Button>
        </TableCell>
      </TableRow>
      <ToDoDrawer
        open={open}
        setOpen={setOpen}
        row={row}
        service={service}
        dependency={dependency}
        vuln={vuln}
        vulnActions={vulnActions}
        bgcolor={bgcolor}
      />
    </>
  );
}

ToDoTableRow.propTypes = {
  row: PropTypes.object.isRequired,
  bgcolor: PropTypes.string.isRequired,
  ssvc: PropTypes.string.isRequired,
  vuln_id: PropTypes.string,
  serviceMap: PropTypes.object.isRequired,
};
