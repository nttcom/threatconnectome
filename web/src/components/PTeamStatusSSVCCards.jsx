import EditIcon from "@mui/icons-material/Edit";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import {
  Box,
  Button,
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
import React, { useState } from "react";
import { useDispatch } from "react-redux";

import { useUpdatePTeamServiceMutation } from "../services/tcApi";
import { getPTeam, getPTeamServiceTagsSummary } from "../slices/pteam";
import {
  sortedSSVCPriorities,
  ssvcPriorityProps,
  sortedSystemExposure,
  systemExposure,
  sortedMissionImpat,
  missionImpact,
} from "../utils/const";
import { errorToString } from "../utils/func";

export function PTeamStatusSSVCCards(props) {
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
  const [isSystemExposureValue, setSystemExposureValue] = useState(service.system_exposure);
  const [isMissionImpactValue, setMissionImpactValue] = useState(service.service_mission_impact);

  const [updatePTeamService] = useUpdatePTeamServiceMutation();
  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();

  const handleUpdatePTeamService = async (card) => {
    console.log(card.title);
    const data =
      card.title === "System Exposure"
        ? { system_exposure: isSystemExposureValue }
        : { service_mission_impact: isMissionImpactValue };
    const serviceId = service.service_id;
    await updatePTeamService({ pteamId, serviceId, data })
      .unwrap()
      .then(() => {
        dispatch(getPTeam(pteamId));
        dispatch(getPTeamServiceTagsSummary({ pteamId: pteamId, serviceId: serviceId }));
        enqueueSnackbar("Update succeeded", { variant: "success" });
      })
      .catch((error) => {
        enqueueSnackbar(`Update failed: ${errorToString(error)}`, { variant: "error" });
      });
  };

  const SSVCCardsList = [
    {
      title: "System Exposure",
      description: "The Accessible Attack Surface of the Affected System or Service.",
      items: sortedSystemExposure,
      valuePairing: systemExposure,
      isEditable: isSystemExposureEditable,
      handleClickIconButton: setIsSystemExposureEditable,
      handleClickToggleButton: setSystemExposureValue,
    },
    {
      title: "Mission Impact",
      description: "Impact on Mission Essential Functions of the Organization.",
      items: sortedMissionImpat,
      valuePairing: missionImpact,
      isEditable: isMissionImpactEditable,
      handleClickIconButton: setIsMissionImpactEditable,
      handleClickToggleButton: setMissionImpactValue,
    },
  ];

  const HighestSSVCPriorityList = {
    title: "Highest SSVC Priority",
    description: "The most serious security issue of the Service.",
    items: sortedSSVCPriorities,
    valuePairing: ssvcPriority,
  };

  return (
    // Create Highest SSVC Priority card
    <Grid container spacing={2}>
      <Grid key={HighestSSVCPriorityList.title} item xs={4}>
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
        <Grid key={card.title} item xs={4}>
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
                    fontWeight: card.title === "Highest SSVC Priority" ? "bold" : "none",
                  }}
                >
                  {card.title}
                </Typography>
                <Tooltip title={card.description}>
                  <HelpOutlineOutlinedIcon color="action" fontSize="small" />
                </Tooltip>
              </Box>
              {!card.isEditable && (
                <IconButton onClick={() => card.handleClickIconButton(true)}>
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
                // value={card.items.filter((item) => SSVCValueList.find((value) => value === item))}
                value={
                  card.title === "System Exposure" ? isSystemExposureValue : isMissionImpactValue
                }
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
                    card.title === "System Exposure"
                      ? card.handleClickToggleButton(service.system_exposure)
                      : card.handleClickToggleButton(service.service_mission_impact);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => {
                    card.handleClickIconButton(false);
                    handleUpdatePTeamService(card);
                  }}
                >
                  Update
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
