import { Typography } from "@mui/material";
import Box from "@mui/material/Box";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Android12Switch } from "../../components/Android12Switch";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

import { CVESearchField } from "./CVESearchField";
import { ToDoTable } from "./ToDoTable";

export function ToDo() {
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const myTasks = params.get("mytasks") === "on" || !params.has("mytasks");
  const cveId = params.get("cve_id")?.trim() ?? "";

  const page = parseInt(params.get("page")) || 1;
  const rowsPerPage = parseInt(params.get("perPage")) || 10;

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

  const updateParams = (newParams) => {
    const updatedParams = new URLSearchParams(location.search);
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === null || value === undefined || value === "") {
        updatedParams.delete(key);
      } else {
        updatedParams.set(key, value);
      }
    });
    navigate(location.pathname + "?" + updatedParams.toString());
  };

  const handleCVESearch = (word) => {
    const newParams = new URLSearchParams(location.search);
    if (word) {
      newParams.set("cve_id", word);
    } else {
      newParams.delete("cve_id");
    }
    if (word !== params.get("cve_id")) {
      newParams.delete("page"); // reset page
    }
    navigate(location.pathname + "?" + newParams.toString());
  };

  const handleMyTasksChange = (event) => {
    const newParams = new URLSearchParams(location.search);

    newParams.set("mytasks", event.target.checked ? "on" : "off");

    newParams.delete("page");
    navigate(location.pathname + "?" + newParams.toString());
  };

  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Android12Switch checked={myTasks} onChange={handleMyTasksChange} />
        <Typography>My tasks</Typography>
      </Box>
      <Box sx={{ mb: 1 }}>
        <CVESearchField word={cveId} onApply={handleCVESearch} />
      </Box>
      <ToDoTable
        myTasks={myTasks}
        pteamIds={pteamIds}
        cveIds={cveId ? [cveId] : []}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={updateParams}
      />
    </>
  );
}
