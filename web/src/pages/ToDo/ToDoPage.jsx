import { Typography, useMediaQuery } from "@mui/material";
import Box from "@mui/material/Box";

import { Android12Switch } from "../../components/Android12Switch";
import { useTodoState } from "../../hooks/ToDo/useTodoState";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

import { CVESearchField } from "./CVESearchField";
import { ToDoTable } from "./ToDoTable";
import VulnerabilityTodoList from "./VulnerabilityTodoList/VulnerabilityTodoList";

export function ToDo() {
  const isMobile = useMediaQuery((theme) => theme.breakpoints.down("md"));

  // All URL state management for the ToDo page is encapsulated in this custom hook.
  // It includes ToDo-specific logic, such as resetting the page on filter/sort changes,
  const {
    myTasks,
    cveId,
    apiParams,
    updateParams,
    handleMyTasksChange,
    handleCVESearch,
    handleSortConfigChange,
    handleItemsPerPageChange,
    handlePageChange,
  } = useTodoState();

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  if (skip) return <></>;
  if (userMeError)
    throw new APIError(errorToString(userMeError), {
      api: "getUserMe",
    });

  if (userMeIsLoading) return <>Now loading UserInfo...</>;
  const pteamIds = userMe?.pteam_roles.map((role) => role.pteam.pteam_id) ?? [];

  return (
    <>
      {isMobile ? (
        <VulnerabilityTodoList
          pteamIds={pteamIds}
          apiParams={apiParams}
          onMyTasksChange={handleMyTasksChange}
          onCveSearch={handleCVESearch}
          onSortConfigChange={handleSortConfigChange}
          onItemsPerPageChange={handleItemsPerPageChange}
          onPageChange={handlePageChange}
        />
      ) : (
        <>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Android12Switch checked={myTasks} onChange={handleMyTasksChange} />
            <Typography>My tasks</Typography>
          </Box>
          <Box sx={{ mb: 1 }}>
            <CVESearchField word={cveId} onApply={handleCVESearch} />
          </Box>
          <ToDoTable pteamIds={pteamIds} onPageChange={updateParams} apiParams={apiParams} />
        </>
      )}
    </>
  );
}
