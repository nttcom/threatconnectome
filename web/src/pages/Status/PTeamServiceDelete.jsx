import {
  Box,
  Button,
  Checkbox,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import styles from "../../cssModule/dialog.module.css";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useDeletePTeamServiceMutation, useGetPTeamQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

export function PTeamServiceDelete(props) {
  const { t } = useTranslation("status", { keyPrefix: "PTeamServiceDelete" });
  const { pteamId, onServiceDeleted } = props;
  const [checked, setChecked] = useState([]);
  const [isDeleting, setIsDeleting] = useState(false);

  const { enqueueSnackbar } = useSnackbar();
  const [deletePTeamService] = useDeletePTeamServiceMutation();
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const serviceId = params.get("serviceId");

  const skip = useSkipUntilAuthUserIsReady() || !pteamId;
  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery({ path: { pteam_id: pteamId } }, { skip });

  if (skip) return <></>;
  if (pteamError)
    throw new APIError(errorToString(pteamError), {
      api: "getPTeam",
    });
  if (pteamIsLoading) return <>{t("loadingTeam")}</>;

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
    setIsDeleting(true);
    try {
      await Promise.all(
        checked.map((service) =>
          deletePTeamService({
            path: { pteam_id: pteamId, service_id: service.service_id },
          }).unwrap(),
        ),
      );

      const serviceCount = checked.length;
      const message = serviceCount === 1 ? t("removeServiceSucceeded") : t("removeServicesSucceeded");

      enqueueSnackbar(message, { variant: "success" });

      const wasCurrentServiceDeleted = checked.find((service) => service.service_id === serviceId);

      const deletedServiceIds = new Set(checked.map((service) => service.service_id));

      if (wasCurrentServiceDeleted) {
        const remainingServices = services.filter(
          (service) => !deletedServiceIds.has(service.service_id),
        );

        if (remainingServices.length > 0) {
          params.set("serviceId", remainingServices[0].service_id);
        } else {
          params.delete("serviceId");
        }
        navigate(location.pathname + "?" + params.toString());
      }

      if (onServiceDeleted) {
        onServiceDeleted();
      }

      setChecked([]);
    } catch (error) {
      const serviceCount = checked.length;
      const failureMessage =
        serviceCount === 1
          ? t("removeServiceFailed", { error: errorToString(error) })
          : t("removeServicesFailed", { error: errorToString(error) });

      enqueueSnackbar(failureMessage, {
        variant: "error",
      });
    } finally {
      setIsDeleting(false);
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
              <ListItemButton
                role={undefined}
                onClick={handleToggle(service)}
                dense
                disabled={isDeleting}
              >
                <ListItemIcon>
                  <Checkbox
                    edge="start"
                    checked={checked.indexOf(service) !== -1}
                    tabIndex={-1}
                    disableRipple
                    disabled={isDeleting}
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
        <Button
          className={isDeleting || checked.length === 0 ? "" : styles.delete_bg_btn}
          onClick={handleDeleteService}
          disabled={isDeleting || checked.length === 0}
          startIcon={isDeleting ? <CircularProgress size={20} /> : null}
          style={{ textTransform: "none" }}
        >
          {isDeleting ? t("deleting") : t("delete")}
        </Button>
      </Box>
    </Box>
  );
}
PTeamServiceDelete.propTypes = {
  pteamId: PropTypes.string.isRequired,
  onServiceDeleted: PropTypes.func,
};
