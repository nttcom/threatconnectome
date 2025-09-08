import { Typography, Box } from "@mui/material";
import PropTypes from "prop-types";

import { Android12Switch } from "../../../components/Android12Switch";
import { CVESearchField } from "../CVESearchField";
import { ToDoTable } from "../ToDoTable";

export function ToDoDesktopView({
  pteamIds,
  apiParams,
  onMyTasksChange,
  onCVESearch,
  onSortConfigChange,
  onPageChange,
  onItemsPerPageChange,
}) {
  const { assignedToMe: myTasks, cveIds } = apiParams;
  const cveId = cveIds && cveIds.length > 0 ? cveIds[0] : "";

  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Android12Switch checked={myTasks} onChange={onMyTasksChange} />
        <Typography>My tasks</Typography>
      </Box>
      <Box sx={{ mb: 1 }}>
        <CVESearchField word={cveId} onApply={onCVESearch} />
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

ToDoDesktopView.propTypes = {
  pteamIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  apiParams: PropTypes.object.isRequired,
  updateParams: PropTypes.func.isRequired,
  onMyTasksChange: PropTypes.func.isRequired,
  onCVESearch: PropTypes.func.isRequired,
  onSortConfigChange: PropTypes.func.isRequired,
  onPageChange: PropTypes.func.isRequired,
  onItemsPerPageChange: PropTypes.func.isRequired,
};
