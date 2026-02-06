import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Box, Button, TableCell, TableRow, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { ResponsiveDrawer } from "../../../components/ResponsiveDrawer";
import { useTodoItemState } from "../../../hooks/ToDo/useTodoItemState";
import { preserveParams } from "../../../utils/urlUtils";
import { TicketDetailView } from "../TicketDetailView";

export function ToDoTableRow(props) {
  const { ticket, ssvcPriority } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "ToDoTableView.ToDoTableRow" });
  const Icon = ssvcPriority.icon;
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const {
    pteam,
    pteamIsLoading,
    service,
    serviceIsLoading,
    vuln,
    vulnIsLoading,
    serviceDependency,
    serviceDependencyIsLoading,
    displayAssignee,
  } = useTodoItemState(ticket);

  const cveId = vuln?.cve_id || t("noKnownCve");
  const pteamName = pteam?.pteam_name || "-";
  const serviceName = service?.service_name || "-";
  const packageName = serviceDependency?.package_name || "-";

  const handleRowClick = () => {
    if (!serviceDependency?.package_id) {
      console.warn("Package ID is not available.");
      return;
    }
    const params = preserveParams(location.search);
    params.set("pteamId", ticket.pteam_id);
    params.set("serviceId", ticket.service_id);
    const packageId = serviceDependency.package_id;
    navigate(`/packages/${packageId}?` + params.toString());
  };

  return (
    <>
      <TableRow hover sx={{ cursor: "pointer" }} onClick={handleRowClick}>
        <TableCell>{vulnIsLoading ? "..." : cveId}</TableCell>
        <TableCell>{pteamIsLoading ? "..." : pteamName}</TableCell>
        <TableCell>{serviceIsLoading ? "..." : serviceName}</TableCell>
        <TableCell>{serviceDependencyIsLoading ? "..." : packageName}</TableCell>
        <TableCell>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography sx={{ pl: 0.5 }}>{displayAssignee}</Typography>
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
            {t("details")}
          </Button>
        </TableCell>
      </TableRow>

      <ResponsiveDrawer
        open={open}
        onClose={() => setOpen(false)}
        title={t("ticketTitle", { ticketId: ticket.ticket_id || "" })}
      >
        <TicketDetailView ticket={ticket} />
      </ResponsiveDrawer>
    </>
  );
}

ToDoTableRow.propTypes = {
  ticket: PropTypes.object.isRequired,
  ssvcPriority: PropTypes.shape({
    icon: PropTypes.elementType.isRequired,
    displayName: PropTypes.string.isRequired,
    style: PropTypes.object.isRequired,
  }).isRequired,
};
