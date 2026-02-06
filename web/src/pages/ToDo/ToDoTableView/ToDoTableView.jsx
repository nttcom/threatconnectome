import { Typography, Box } from "@mui/material";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { Android12Switch } from "../../../components/Android12Switch";
import { CVESearchField } from "../CVESearchField";

import { ToDoTable } from "./ToDoTable";

export function ToDoTableView({
  pteamIds,
  apiParams,
  onMyTasksChange,
  onCveSearch,
  onSortConfigChange,
  onPageChange,
  onItemsPerPageChange,
}) {
  const { t } = useTranslation("toDo", { keyPrefix: "ToDoTableView.ToDoTableView" });
  const { assigned_to_me: myTasks, cve_ids: cveIds } = apiParams;
  const cveId = cveIds?.[0] ?? "";

  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Android12Switch checked={myTasks} onChange={onMyTasksChange} />
        <Typography>{t("myTasks")}</Typography>
      </Box>
      <Box sx={{ mb: 1 }}>
        <CVESearchField word={cveId} onApply={onCveSearch} />
      </Box>
      <ToDoTable
        pteamIds={pteamIds}
        apiParams={apiParams}
        onSortConfigChange={onSortConfigChange}
        onPageChange={onPageChange}
        onItemsPerPageChange={onItemsPerPageChange}
      />
    </>
  );
}

ToDoTableView.propTypes = {
  pteamIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  apiParams: PropTypes.object.isRequired,
  onMyTasksChange: PropTypes.func.isRequired,
  onCveSearch: PropTypes.func.isRequired,
  onSortConfigChange: PropTypes.func.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onItemsPerPageChange: PropTypes.func.isRequired,
};
