import {
  Box,
  Card,
  CardActions,
  CardContent,
  Divider,
  Pagination,
  Skeleton,
  Stack,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { Android12Switch } from "../../../components/Android12Switch";
import { useGetTicketsQuery } from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";
import { CVESearchField } from "../CVESearchField";

import { DisplayOptionsController } from "./DisplayOptionsController";
import { VulnerabilityCard } from "./VulnerabilityCard";

export default function ToDoCardView({
  pteamIds,
  apiParams,
  onMyTasksChange,
  onCveSearch,
  onSortConfigChange,
  onItemsPerPageChange,
  onPageChange,
}) {
  const { t } = useTranslation("toDo", { keyPrefix: "ToDoCardView.ToDoCardView" });
  const {
    page,
    sortConfig,
    assigned_to_me: myTasks,
    cve_ids: cveIds,
    limit: itemsPerPage,
  } = apiParams;
  const cveId = cveIds?.[0] ?? "";

  const {
    data: ticketsData,
    error: ticketsError,
    isLoading: ticketsIsLoading,
  } = useGetTicketsQuery({
    query: { ...apiParams, pteam_ids: pteamIds },
  });

  const tickets = ticketsData?.tickets ?? [];

  const pageCount = Math.ceil((ticketsData?.total ?? 0) / itemsPerPage);

  const paginationComponent = (
    <Pagination
      count={pageCount}
      page={page}
      onChange={onPageChange}
      color="primary"
      size="small"
      siblingCount={0}
    />
  );

  if (ticketsError) {
    throw new APIError(errorToString(ticketsError), { api: "getTickets" });
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Box sx={{ mb: 3 }}>
        <CVESearchField word={cveId} onApply={onCveSearch} variant="mobile" />
      </Box>

      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Android12Switch checked={myTasks} onChange={onMyTasksChange} />
          <Typography>{t("myTasks")}</Typography>
        </Box>
        <DisplayOptionsController
          sortConfig={sortConfig}
          onSortConfigChange={onSortConfigChange}
          itemsPerPage={itemsPerPage}
          onItemsPerPageChange={onItemsPerPageChange}
        />
      </Box>

      <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>{paginationComponent}</Box>

      {ticketsIsLoading ? (
        <Stack spacing={3}>
          {[...Array(3)].map((_, index) => (
            <Card key={index} sx={{ borderRadius: 5, border: "2px solid rgba(0, 0, 0, 0.15)" }}>
              <CardContent sx={{ pt: 3, px: 3 }}>
                <Skeleton variant="text" sx={{ fontSize: "1.5rem", width: "60%" }} />
                <Divider sx={{ my: 2 }} />
                <Skeleton variant="rectangular" sx={{ height: 100 }} />
              </CardContent>
              <CardActions sx={{ p: 2, justifyContent: "flex-end" }}>
                <Skeleton variant="rounded" sx={{ width: 120, height: 40 }} />
              </CardActions>
            </Card>
          ))}
        </Stack>
      ) : tickets.length > 0 ? (
        <Stack spacing={3}>
          {tickets.map((ticket) => (
            <VulnerabilityCard key={ticket.ticket_id} ticket={ticket} />
          ))}
        </Stack>
      ) : (
        <Box sx={{ textAlign: "center", py: 5 }}>
          <Typography color="text.secondary">{t("noTasksFound")}</Typography>
        </Box>
      )}

      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>{paginationComponent}</Box>
    </Box>
  );
}

ToDoCardView.propTypes = {
  pteamIds: PropTypes.arrayOf(PropTypes.string),
  apiParams: PropTypes.object.isRequired,
  onMyTasksChange: PropTypes.func.isRequired,
  onCveSearch: PropTypes.func.isRequired,
  onSortConfigChange: PropTypes.func.isRequired,
  onItemsPerPageChange: PropTypes.func.isRequired,
  onPageChange: PropTypes.func.isRequired,
};
