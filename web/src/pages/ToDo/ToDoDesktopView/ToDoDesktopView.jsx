import { Typography, Box } from "@mui/material";
import PropTypes from "prop-types";

import { Android12Switch } from "../../../components/Android12Switch";
import { CVESearchField } from "../CVESearchField";
import { ToDoTable } from "../ToDoTable";

export function ToDoDesktopView({
  pteamIds,
  apiParams,
  updateParams,
  onMyTasksChange,
  onCVESearch,
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
      <ToDoTable pteamIds={pteamIds} onPageChange={updateParams} apiParams={apiParams} />
    </>
  );
}

ToDoDesktopView.propTypes = {
  pteamIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  apiParams: PropTypes.object.isRequired,
  updateParams: PropTypes.func.isRequired,
  onMyTasksChange: PropTypes.func.isRequired,
  onCVESearch: PropTypes.func.isRequired,
};
