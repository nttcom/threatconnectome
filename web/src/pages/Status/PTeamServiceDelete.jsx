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
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import styles from "../../cssModule/dialog.module.css";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useDeletePTeamServiceMutation, useGetPTeamQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

export function PTeamServiceDelete(props) {
  const { pteamId } = props;
  const [checked, setChecked] = useState([]);

  const { enqueueSnackbar } = useSnackbar();
  const [deletePTeamService] = useDeletePTeamServiceMutation();
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const serviceId = params.get("serviceId");

  const skip = useSkipUntilAuthUserIsReady() || !!pteamId;
  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, { skip });

  if (skip) return <></>;
  if (pteamError)
    throw new APIError(errorToString(pteamError), {
      api: "getPTeam",
    });
  if (pteamIsLoading) return <>Now loading Team...</>;

  const services = pteam.services;

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
    function onSuccess(success) {
      enqueueSnackbar("Remove service succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Remove service failed: ${errorToString(error)}`, {
        variant: "error",
      });
    }
    checked.map(
      async (service) =>
        await deletePTeamService({ pteamId: pteamId, serviceName: service.service_name })
          .unwrap()
          .then((success) => onSuccess(success))
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
PTeamServiceDelete.propTypes = {
  pteamId: PropTypes.string.isRequired,
};
