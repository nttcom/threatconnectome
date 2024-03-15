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
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { UUIDTypography } from "../components/UUIDTypography";
import { updateUser } from "../slices/user";

export function Account() {
  const [editInfo, setEditInfo] = useState({
    years: 0,
  });
  const [editMode, setEditMode] = useState(false);

  const dispatch = useDispatch();
  const user = useSelector((state) => state.user.user);

  useEffect(() => {
    if (!user?.user_id) return;
    setEditInfo({ years: user.years });
  }, [dispatch, user]);

  useEffect(() => {
    if (!user.user_id) return;
  }, [dispatch, user]);

  const handleEditMode = () => {
    setEditInfo({ years: user.years });
    setEditMode(!editMode);
  };

  const handleSave = async () => {
    dispatch(
      updateUser({
        userId: user.user_id,
        user: { years: editInfo.years },
      }),
    );
    handleEditMode();
  };

  return (
    user && (
      <>
        <Box display="flex" flexDirection="row" flexGrow={1} mb={1}>
          <Box display="flex" flexDirection="column" flexGrow={1}>
            <Box alignItems="baseline" display="flex" flexDirection="row">
              <Typography variant="h4">{user.email?.split("@")[0]}</Typography>
              <Typography color={grey[500]} variant="subtitle">
                {`@${user.email?.split("@")[1]}`}
              </Typography>
            </Box>
            <UUIDTypography>{user.user_id}</UUIDTypography>
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
            <Typography>{user.email}</Typography>
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" mt={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>User ID:</Typography>
          </Box>
          <Box display="flex" flexDirection="row" width="70%">
            <Typography>{user.user_id}</Typography>
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" my={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>PTeam:</Typography>
          </Box>
          <Box display="flex" flexDirection="column" width="70%">
            {user.pteams?.length >= 1 ? (
              user.pteams.map((pteam, index) => (
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
        <Box alignItems="center" display="flex" flexDirection="row" my={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>ATeam:</Typography>
          </Box>
          <Box display="flex" flexDirection="column" width="70%">
            {user.ateams?.length >= 1 ? (
              user.ateams.map((ateam, index) => (
                <Box alignItems="baseline" display="flex" flexDirection="row" key={index}>
                  <Typography mr={1}>{ateam.ateam_name}</Typography>
                  <UUIDTypography>{ateam.ateam_id}</UUIDTypography>
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
                {user.years}+ year{user.years <= 1 ? "" : "s"}
              </Typography>
            )}
          </Box>
        </Box>
      </>
    )
  );
}
