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

import {
  sortedSSVCPriorities,
  ssvcPriorityProps,
  sortedSystemExposure,
  systemExposure,
  sortedMissionImpat,
  missionImpact,
} from "../utils/const";

export function PTeamStatusSSVCCards(props) {
  const { service, highestSsvcPriority } = props;
  const SSVCValueList = [
    highestSsvcPriority,
    service.system_exposure,
    service.service_mission_impact,
  ];
  const ssvcPriorityProp = ssvcPriorityProps[highestSsvcPriority];
  const Icon = ssvcPriorityProp.icon;

  let ssvcPriority = {
    ...ssvcPriorityProps,
  };
  Object.keys(ssvcPriorityProps).forEach((key) => {
    ssvcPriority[key] = ssvcPriorityProps[key]["displayName"];
  });

  const HighestSSVCPriorityList = {
    title: "Highest SSVC Priority",
    description: "The most serious security issue of the Service.",
    items: sortedSSVCPriorities,
    valuePairing: ssvcPriority,
  };

  const [isSystemExposureEditable, setIsSystemExposureEditable] = useState(false);
  const [isMissionImpactEditable, setIsMissionImpactEditable] = useState(false);
  const SSVCCardsList = [
    {
      title: "System Exposure",
      description: "The Accessible Attack Surface of the Affected System or Service.",
      items: sortedSystemExposure,
      valuePairing: systemExposure,
      isEditable: isSystemExposureEditable,
      handleClick: setIsSystemExposureEditable,
    },
    {
      title: "Mission Impact",
      description: "Impact on Mission Essential Functions of the Organization.",
      items: sortedMissionImpat,
      valuePairing: missionImpact,
      isEditable: isMissionImpactEditable,
      handleClick: setIsMissionImpactEditable,
    },
  ];

  const { enqueueSnackbar } = useSnackbar();

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
                <IconButton onClick={() => card.handleClick(true)}>
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
                value={card.items.filter((item) => SSVCValueList.find((value) => value === item))}
              >
                {card.items.map((item) => (
                  <ToggleButton key={item} value={item} disabled={card.isEditable ? false : true}>
                    {card.valuePairing[item]}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>
            {card.isEditable && (
              <Stack direction="row" spacing={1} sx={{ mx: 1, mb: 1, justifyContent: "end" }}>
                <Button size="small" onClick={() => card.handleClick(false)}>
                  Cancel
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  disabled
                  onClick={() => {
                    enqueueSnackbar("update succeeded", { variant: "success" });
                    card.handleClick(false);
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
  service: PropTypes.object.isRequired,
  highestSsvcPriority: PropTypes.string.isRequired,
};
