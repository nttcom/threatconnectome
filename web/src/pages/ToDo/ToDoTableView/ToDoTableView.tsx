import { Typography, Box } from "@mui/material";
import { useTranslation } from "react-i18next";

import { Android12Switch } from "../../../components/Android12Switch";
import { CVESearchField } from "../CVESearchField";
import type { TodoViewProps } from "../todoViewProps";

import { ToDoTable } from "./ToDoTable";

export function ToDoTableView({
  pteamIds,
  apiParams,
  onMyTasksChange,
  onCveSearch,
  onSortConfigChange,
  onPageChange,
  onItemsPerPageChange,
}: TodoViewProps) {
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
