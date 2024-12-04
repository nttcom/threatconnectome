import { Edit as EditIcon, Save as SaveIcon, Undo as UndoIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  ButtonGroup,
  Divider,
  MenuItem,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import React, { useState } from "react";

import { UUIDTypography } from "../components/UUIDTypography";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetUserMeQuery, useUpdateUserMutation } from "../services/tcApi";
import { errorToString } from "../utils/func";

export function Account() {
  const [editInfo, setEditInfo] = useState({
    years: 0,
  });
  const [editMode, setEditMode] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const [updateUser] = useUpdateUserMutation();
  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  if (skip) return <></>;
  if (userMeError) return <>{`Cannot get user info: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const handleEditMode = () => {
    setEditInfo({ years: userMe.years });
    setEditMode(!editMode);
  };

  const handleSave = async () => {
    updateUser({
      userId: userMe.user_id,
      data: { years: editInfo.years },
    })
      .unwrap()
      .then((succeeded) => {
        enqueueSnackbar("Update user info succeeded", { variant: "success" });
        handleEditMode();
      })
      .catch((error) => enqueueSnackbar(errorToString(error), { variant: "error" }));
  };

  return (
    userMe && (
      <>
        <Box display="flex" flexDirection="row" flexGrow={1} mb={1}>
          <Box display="flex" flexDirection="column" flexGrow={1}>
            <Box alignItems="baseline" display="flex" flexDirection="row">
              <Typography variant="h4">{userMe.email?.split("@")[0]}</Typography>
              <Typography color={grey[500]} variant="subtitle">
                {`@${userMe.email?.split("@")[1]}`}
              </Typography>
            </Box>
            <UUIDTypography>{userMe.user_id}</UUIDTypography>
          </Box>
          <Box justifyContent="center" display="flex" flexDirection="column">
            <ButtonGroup>
              {editMode && (
                <Tooltip arrow placement="bottom-end" title="Save">
                  <Button color="success" onClick={handleSave} variant="contained">
                    <SaveIcon />
                  </Button>
                </Tooltip>
              )}
              <Tooltip
                arrow
                placement="bottom-end"
                title={editMode ? "Exit Edit Mode" : "Edit Account Info"}
              >
                <Button color="warning" onClick={handleEditMode} variant="contained">
                  {editMode ? <UndoIcon /> : <EditIcon />}
                </Button>
              </Tooltip>
            </ButtonGroup>
          </Box>
        </Box>
        <Divider />
        <Box alignItems="center" display="flex" flexDirection="row" mt={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>Email:</Typography>
          </Box>
          <Box display="flex" flexDirection="row" width="70%">
            <Typography>{userMe.email}</Typography>
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" mt={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>User ID:</Typography>
          </Box>
          <Box display="flex" flexDirection="row" width="70%">
            <Typography>{userMe.user_id}</Typography>
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" my={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>PTeam:</Typography>
          </Box>
          <Box display="flex" flexDirection="column" width="70%">
            {userMe.pteams?.length >= 1 ? (
              userMe.pteams.map((pteam, index) => (
                <Box alignItems="baseline" display="flex" flexDirection="row" key={index}>
                  <Typography mr={1}>{pteam.pteam_name}</Typography>
                  <UUIDTypography>{pteam.pteam_id}</UUIDTypography>
                </Box>
              ))
            ) : (
              <Typography>-</Typography>
            )}
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" mt={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Tooltip
              arrow
              title="Please select years of your work experience in security to support security response."
            >
              <Typography>Years of work experience in security:</Typography>
            </Tooltip>
          </Box>
          <Box display="flex" flexDirection="row" width="70%">
            {editMode ? (
              <TextField
                fullWidth
                label="Years of work experience in security:"
                margin="dense"
                onChange={(event) => setEditInfo({ ...editInfo, years: event.target.value })}
                select
                size="small"
                value={editInfo.years}
              >
                <MenuItem value={0}>0+ year</MenuItem>
                <MenuItem value={2}>2+ years</MenuItem>
                <MenuItem value={5}>5+ years</MenuItem>
                <MenuItem value={7}>7+ years</MenuItem>
              </TextField>
            ) : (
              <Typography>
                {userMe.years}+ year{userMe.years <= 1 ? "" : "s"}
              </Typography>
            )}
          </Box>
        </Box>
      </>
    )
  );
}
