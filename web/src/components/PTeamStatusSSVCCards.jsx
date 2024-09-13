import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import {
  Box,
  Grid,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

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

  let ssvcPriority = {
    ...ssvcPriorityProps,
  };
  Object.keys(ssvcPriorityProps).forEach((key) => {
    ssvcPriority[key] = ssvcPriorityProps[key]["displayName"];
  });

  const SSVCCardsList = [
    {
      title: "Highest SSVC Priority",
      description: "The most serious security issue of the Service.",
      items: sortedSSVCPriorities,
      valuePairing: ssvcPriority,
    },
    {
      title: "System Exposure",
      description: "The Accessible Attack Surface of the Affected System or Service.",
      items: sortedSystemExposure,
      valuePairing: systemExposure,
    },
    {
      title: "Mission Impact",
      description: "Impact on Mission Essential Functions of the Organization.",
      items: sortedMissionImpat,
      valuePairing: missionImpact,
    },
  ];

  return (
    <Grid container spacing={2}>
      {SSVCCardsList.map((card) => (
        <Grid key={card.title} item xs={4}>
          <Paper
            sx={{
              textAlign: "center",
              height: "100%",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", my: 1 }}>
              <Typography variant="h6" component="div" sx={{ pr: 0.5 }}>
                {card.title}
              </Typography>
              <Tooltip title={card.description}>
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
                color="primary"
                size="small"
                orientation="vertical"
                value={card.items.filter((item) => SSVCValueList.find((value) => value === item))}
              >
                {card.items.map((item) => (
                  <ToggleButton key={item} value={item} disabled>
                    {card.valuePairing[item]}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
            </Box>
          </Paper>
        </Grid>
      ))}
    </Grid>
  );
}

PTeamStatusSSVCCards.propTypes = {
  service: PropTypes.object.isRequired,
  highestSsvcPriority: PropTypes.object.isRequired,
};
