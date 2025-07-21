import { Typography } from "@mui/material";
import Box from "@mui/material/Box";
import { useEffect, useState } from "react";

import { Android12Switch } from "../../components/Android12Switch";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

import { ToDoTable } from "./ToDoTable";

export function ToDo() {
  const [myTasks, setMyTasks] = useState(() => {
    const saved = localStorage.getItem("myTasks");

    switch (saved) {
      case null:
        return true;
      case "true":
        return true;
      case "false":
        return false;
      default:
        return true;
    }
  });

  useEffect(() => {
    localStorage.setItem("myTasks", myTasks);
  }, [myTasks]);

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
      <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
        <Android12Switch checked={myTasks} onChange={(event) => setMyTasks(event.target.checked)} />
        <Typography>My tasks</Typography>
      </Box>

      <ToDoTable myTasks={myTasks} pteamIds={pteamIds} />
    </>
  );
}
