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
import React from "react";

export function PTeamStatusSSVCCards() {
  const SSVCCardsList = [
    {
      title: "Highest SSVC Priority",
      description: "Highest SSVC Priority description",
      item: ["Immediate", "Out-of-Cycle", "Scheduled", "Defer"],
    },
    {
      title: "System Exposure",
      description: "System Exposure description",
      item: ["Small", "Controlled", "Open"],
    },
    {
      title: "Mission Impact",
      description: "Mission Impact description",
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
                value={card.item[0]}
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
