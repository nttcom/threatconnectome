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

export function PTeamStatusSSVCCards(props) {
  const { service, serviceTagsSummary } = props;

  let highestSSVCPriority = serviceTagsSummary.tags[0].ssvc_priority;
  if (highestSSVCPriority === null) {
    highestSSVCPriority = "defer";
  }

  const SSVCValueList = [
    highestSSVCPriority,
    service.system_exposure,
    service.service_mission_impact,
  ];

  const SSVCCardsList = [
    {
      title: "Highest SSVC Priority",
      description: "The most serious security issue of the Service.",
      item: ["Immediate", "Out-of-Cycle", "Scheduled", "Defer"],
    },
    {
      title: "System Exposure",
      description: "The Accessible Attack Surface of the Affected System or Service.",
      item: ["Small", "Controlled", "Open"],
    },
    {
      title: "Mission Impact",
      description: "Impact on Mission Essential Functions of the Organization.",
      item: ["Degraded", "MEF Support Crippled", "MEF Failure", "Mission Failure"],
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
                value={card.item.filter((item) =>
                  SSVCValueList.find(
                    (value) =>
                      value === item.toLocaleLowerCase().replace(/ /g, "_").replace(/-/g, "_"),
                  ),
                )}
              >
                {card.item.map((item) => (
                  <ToggleButton key={item} value={item} disabled>
                    {item}
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
  serviceTagsSummary: PropTypes.object.isRequired,
};
