import EditIcon from "@mui/icons-material/Edit";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import {
  Box,
  Button,
  CircularProgress,
  Grid,
  IconButton,
  Paper,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

import { useUpdatePTeamServiceMutation } from "../../services/tcApi";
import {
  sortedSystemExposure,
  systemExposure,
  sortedMissionImpact,
  missionImpact,
} from "../../utils/const";
import { errorToString } from "../../utils/func";
import { sortedSSVCPriorities, ssvcPriorityProps } from "../../utils/ssvcUtils";

export function PTeamStatusSSVCCards(props) {
  const { t } = useTranslation("status", { keyPrefix: "PTeamStatusSSVCCards" });
  const { pteamId, service, highestSsvcPriority } = props;
  const ssvcPriorityProp = ssvcPriorityProps[highestSsvcPriority];
  const Icon = ssvcPriorityProp.icon;

  let ssvcPriority = {
    ...ssvcPriorityProps,
  };
  Object.keys(ssvcPriorityProps).forEach((key) => {
    ssvcPriority[key] = ssvcPriorityProps[key]["displayName"];
  });

  const [isSystemExposureEditable, setIsSystemExposureEditable] = useState(false);
  const [isMissionImpactEditable, setIsMissionImpactEditable] = useState(false);
  const [systemExposureValue, setSystemExposureValue] = useState(service.system_exposure);
  const [missionImpactValue, setMissionImpactValue] = useState(service.service_mission_impact);
  const [isUpdating, setIsUpdating] = useState(false);

  const [updatePTeamService] = useUpdatePTeamServiceMutation();
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    setIsSystemExposureEditable(false);
    setIsMissionImpactEditable(false);
    setSystemExposureValue(service.system_exposure);
    setMissionImpactValue(service.service_mission_impact);
    setIsUpdating(false);
  }, [service]);

  const handleUpdatePTeamService = async (card) => {
    setIsUpdating(true);
    const data =
      card.title === "System Exposure"
        ? { system_exposure: systemExposureValue }
        : { service_mission_impact: missionImpactValue };
    const serviceId = service.service_id;
    await updatePTeamService({ path: { pteam_id: pteamId, service_id: serviceId }, body: data })
      .unwrap()
      .then(() => {
        enqueueSnackbar(t("updateSucceeded"), { variant: "success" });
        card.handleClickIconButton(false);
      })
      .catch((error) => {
        enqueueSnackbar(t("updateFailed", { error: errorToString(error) }), { variant: "error" });
      })
      .finally(() => {
        setIsUpdating(false);
      });
  };

  const SSVCCardsList = [
    {
      title: t("systemExposure"),
      description: t("systemExposureDesc"),
      items: sortedSystemExposure,
      valuePairing: systemExposure,
      isEditable: isSystemExposureEditable,
      handleClickIconButton: setIsSystemExposureEditable,
      handleClickToggleButton: setSystemExposureValue,
    },
    {
      title: t("missionImpact"),
      description: t("missionImpactDesc"),
      items: sortedMissionImpact,
      valuePairing: missionImpact,
      isEditable: isMissionImpactEditable,
      handleClickIconButton: setIsMissionImpactEditable,
      handleClickToggleButton: setMissionImpactValue,
    },
  ];

  const HighestSSVCPriorityList = {
    title: t("highestSSVCPriority"),
    description: t("highestSSVCPriorityDesc"),
    items: sortedSSVCPriorities,
    valuePairing: ssvcPriority,
  };

  return (
    // Create Highest SSVC Priority card
    <Grid container spacing={2}>
      <Grid key={HighestSSVCPriorityList.title} size={{ xs: 4 }}>
        <Paper
          sx={{
            textAlign: "center",
            height: "100%",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", my: 1 }}>
            <Typography
              variant="h6"
              component="div"
              sx={{
                pr: 0.5,
                fontWeight: "bold",
              }}
            >
              {HighestSSVCPriorityList.title}
            </Typography>
            <Tooltip title={HighestSSVCPriorityList.description}>
              <HelpOutlineOutlinedIcon color="action" fontSize="small" />
            </Tooltip>
          </Box>
          <Box
            sx={{
              display: "flex",
              height: "100%",
              justifyContent: "center",
              alignItems: "center",
              mb: 1,
            }}
          >
            <ToggleButtonGroup
              size="small"
              orientation="vertical"
              value={highestSsvcPriority}
              sx={{
                "& .MuiToggleButton-root": {
                  width: "100%",
                  "&.Mui-selected": {
                    backgroundColor: ssvcPriorityProps[highestSsvcPriority].style.bgcolor,
                  },
                },
              }}
            >
              {HighestSSVCPriorityList.items.map((item) =>
                item === highestSsvcPriority ? (
                  <ToggleButton key={item} value={item} sx={{ padding: "0" }} disabled>
                    <Button component="div" startIcon={<Icon />} sx={{ color: "white" }}>
                      {HighestSSVCPriorityList.valuePairing[item]}
                    </Button>
                  </ToggleButton>
                ) : (
                  <ToggleButton key={item} value={item} sx={{ padding: "0" }} disabled>
                    <Button component="div" disabled>
                      {HighestSSVCPriorityList.valuePairing[item]}
                    </Button>
                  </ToggleButton>
                ),
              )}
            </ToggleButtonGroup>
          </Box>
        </Paper>
      </Grid>

      {SSVCCardsList.map((card) => (
        // Create System Exposure card and Mission Impact
        <Grid key={card.title} size={{ xs: 4 }}>
          <Paper
            sx={{
              textAlign: "center",
              height: "100%",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: "50px auto 50px",
                justifyItems: "center",
                alignItems: "center",
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  my: 1,
                  gridColumn: 2,
                }}
              >
                <Typography
                  variant="h6"
                  component="div"
                  sx={{
                    pr: 0.5,
                    fontWeight: "none",
                  }}
                >
                  {card.title}
                </Typography>
                <Tooltip title={card.description}>
                  <HelpOutlineOutlinedIcon color="action" fontSize="small" />
                </Tooltip>
              </Box>
              {!card.isEditable && (
                <IconButton
                  disabled={isUpdating || isSystemExposureEditable || isMissionImpactEditable}
                  onClick={() => card.handleClickIconButton(true)}
                >
                  <EditIcon />
                </IconButton>
              )}
            </Box>
            <Box
              sx={{
                display: "flex",
                height: "100%",
                justifyContent: "center",
                alignItems: "center",
                mb: 1,
              }}
            >
              <ToggleButtonGroup
                size="small"
                color="primary"
                orientation="vertical"
                value={card.title === "System Exposure" ? systemExposureValue : missionImpactValue}
              >
                {card.items.map((item) => (
                  <ToggleButton
                    key={item}
                    value={item}
                    disabled={card.isEditable ? false : true}
                    onClick={() => {
                      card.handleClickToggleButton(item);
                    }}
                  >
                    {card.valuePairing[item]}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>
            {card.isEditable && (
              <Stack direction="row" spacing={1} sx={{ mx: 1, mb: 1, justifyContent: "end" }}>
                <Button
                  size="small"
                  onClick={() => {
                    card.handleClickIconButton(false);
                    card.title === t("systemExposure")
                      ? card.handleClickToggleButton(service.system_exposure)
                      : card.handleClickToggleButton(service.service_mission_impact);
                  }}
                  disabled={isUpdating}
                >
                  {t("cancel")}
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => {
                    handleUpdatePTeamService(card);
                  }}
                  disabled={isUpdating}
                  startIcon={isUpdating ? <CircularProgress size={20} /> : null}
                >
                  {isUpdating ? t("updating") : t("update")}
                </Button>
              </Stack>
            )}
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
}

PTeamStatusSSVCCards.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
  highestSsvcPriority: PropTypes.string.isRequired,
};
