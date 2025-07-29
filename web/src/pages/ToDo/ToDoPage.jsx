import SearchIcon from "@mui/icons-material/Search";
import { InputAdornment, TextField, Typography, useTheme } from "@mui/material";
import Box from "@mui/material/Box";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Android12Switch } from "../../components/Android12Switch";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

import { ToDoTable } from "./ToDoTable";

function CVESearchField(props) {
  const { word, onApply } = props;
  const [newWord, setNewWord] = useState(word);
  const { enqueueSnackbar } = useSnackbar();

  const CVE_PATTERN = /^CVE-\d{4}-\d{4,}$/;

  const handleApply = (value) => {
    const trimmedValue = value.trim();

    if (trimmedValue && !CVE_PATTERN.test(trimmedValue)) {
      enqueueSnackbar("Invalid CVE ID format. Expected format: CVE-YYYY-NNNN", {
        variant: "error",
      });
      return;
    }

    onApply(trimmedValue);
  };

  return (
    <>
      <TextField
        size="small"
        type="search"
        placeholder="Search CVE ID"
        hiddenLabel
        fullWidth
        value={newWord}
        onChange={(event) => setNewWord(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            handleApply(event.target.value);
          }
        }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />
    </>
  );
}

CVESearchField.propTypes = {
  word: PropTypes.string.isRequired,
  onApply: PropTypes.func.isRequired,
};

export function ToDo() {
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const myTasks = params.get("mytasks") === "off" ? false : true;
  const cveId = params.get("cve_id")?.trim() ?? "";

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

  const handleCVESearch = (word) => {
    const newParams = new URLSearchParams(location.search);
    if (word) {
      newParams.set("cve_id", word);
    } else {
      newParams.delete("cve_id");
    }
    if (word !== params.get("cve_id")) {
      newParams.set("page", 1); // reset page
    }
    navigate(location.pathname + "?" + newParams.toString());
  };

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
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Android12Switch checked={myTasks} onChange={handleMyTasksChange} />
        <Typography>My tasks</Typography>
      </Box>
      <Box sx={{ mb: 1 }}>
        <CVESearchField word={cveId} onApply={handleCVESearch} />
      </Box>
      <ToDoTable myTasks={myTasks} pteamIds={pteamIds} cveIds={cveId ? [cveId] : []} />
    </>
  );
}
