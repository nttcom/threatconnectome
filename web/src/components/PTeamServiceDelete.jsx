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
import { useLocation, useNavigate } from "react-router";

import styles from "../cssModule/dialog.module.css";
import { getPTeam, invalidateServiceId } from "../slices/pteam";
import { deletePTeamService } from "../utils/api.js";

export function PTeamServiceDelete() {
  const [checked, setChecked] = useState([]);

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const services = useSelector((state) => state.pteam.pteam.services);

  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const serviceId = params.get("serviceId");

  const handleToggle = (service) => () => {
    const currentIndex = checked.indexOf(service);
    const newChecked = [...checked];

    if (currentIndex === -1) {
      newChecked.push(service);
    } else {
      newChecked.splice(currentIndex, 1);
    }

    setChecked(newChecked);
  };

  const handleDeleteService = async () => {
    function onSuccess(success, deletingServiceId) {
      dispatch(getPTeam(pteamId)); // sync pteam.services
      dispatch(invalidateServiceId(deletingServiceId));
      enqueueSnackbar("Remove service succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Remove service failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    checked.map(
      async (service) =>
        await deletePTeamService(pteamId, service.service_name)
          .then((success) => onSuccess(success, service.service_id))
          .catch((error) => onError(error)),
    );
    if (checked.find((service) => service.service_id === serviceId)) {
      params.delete("serviceId"); // current selected serviceId is obsoleted!
      navigate(location.pathname + "?" + params.toString()); // entrust to default behavior
    }
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
          const labelId = `checkbox-list-label-${service.service_name}`;
          return (
            <ListItem key={service.service_id} disablePadding>
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
                <ListItemText id={labelId} primary={service.service_name} />
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
