import {
  Box,
  Button,
  Checkbox,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";

import styles from "../cssModule/dialog.module.css";
import { getPTeamGroups, getPTeamTagsSummary } from "../slices/pteam";
import { deletePTeamService } from "../utils/api.js";

export function PTeamServiceDelete() {
  const [checked, setChecked] = useState([]);

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const services = useSelector((state) => state.pteam.groups);

  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();

  const handleToggle = (value) => () => {
    const currentIndex = checked.indexOf(value);
    const newChecked = [...checked];

    if (currentIndex === -1) {
      newChecked.push(value);
    } else {
      newChecked.splice(currentIndex, 1);
    }

    setChecked(newChecked);
  };

  const handleDeleteService = async () => {
    function onSuccess(success) {
      dispatch(getPTeamTagsSummary(pteamId));
      dispatch(getPTeamGroups(pteamId));
      enqueueSnackbar("Remove service succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Remove service failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    checked.map(
      async (service) =>
        await deletePTeamService(pteamId, service)
          .then((success) => onSuccess(success))
          .catch((error) => onError(error)),
    );
  };

  return (
    <Box>
      <List
        sx={{
          width: "98%",
          position: "relative",
          overflow: "auto",
          maxHeight: 200,
        }}
      >
        {services.map((service) => {
          const labelId = `checkbox-list-label-${service}`;
          return (
            <ListItem key={service} disablePadding>
              <ListItemButton role={undefined} onClick={handleToggle(service)} dense>
                <ListItemIcon>
                  <Checkbox
                    edge="start"
                    checked={checked.indexOf(service) !== -1}
                    tabIndex={-1}
                    disableRipple
                    inputProps={{ "aria-labelledby": labelId }}
                  />
                </ListItemIcon>
                <ListItemText id={labelId} primary={service} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      <Divider sx={{ mt: 5 }} />
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <Button className={styles.delete_bg_btn} onClick={handleDeleteService}>
          Delete
        </Button>
      </Box>
    </Box>
  );
}
