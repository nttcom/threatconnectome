import { Typography } from "@mui/material";
import Box from "@mui/material/Box";
import { useLocation, useNavigate } from "react-router-dom";

import { Android12Switch } from "../../components/Android12Switch";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

import { ToDoTable } from "./ToDoTable";

export function ToDo() {
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const myTasks = params.get("mytasks") === "off" ? false : true;

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

  const handleMyTasksChange = (event) => {
    const newParams = new URLSearchParams(location.search);

    if (event.target.checked) {
      newParams.delete("mytasks");
    } else {
      newParams.set("mytasks", "off");
    }

    navigate(location.pathname + "?" + newParams.toString());
  };

  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
        <Android12Switch checked={myTasks} onChange={handleMyTasksChange} />
        <Typography>My tasks</Typography>
      </Box>

      <ToDoTable myTasks={myTasks} pteamIds={pteamIds} />
    </>
  );
}
