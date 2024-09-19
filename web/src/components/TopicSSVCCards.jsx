import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import {
  Box,
  Card,
  Grid,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import React from "react";

export function TopicSSVCCards() {
  const decisionPoints = [
    {
      name: "Automatable",
      description:
        "Can an attacker reliably automate creating exploitation events for this vulnerability?",
      values: [
        {
          name: "No",
          description:
            "No: Attackers cannot reliably automate steps 1-4 of the kill chain for this vulnerability. These steps are (1) reconnaissance, (2) weaponization, (3) delivery, and (4) exploitation.",
        },
        {
          name: "Yes",
          description: "Yes: Attackers can reliably automate steps 1-4 of the kill chain.",
        },
      ],
    },
    {
      name: "Exploitation",
      description: "The present state of exploitation of the vulnerability.",
      values: [
        {
          name: "None",
          description:
            "None: There is no evidence of active exploitation and no public proof of concept (PoC) of how to exploit the vulnerability.",
        },
        {
          name: "Public PoC",
          description:
            "Public PoC: One of the following is true: (1) Typical public PoC exists in sources such as Metasploit or websites like ExploitDB; or (2) the vulnerability has a well-known method of exploitation.",
        },
        {
          name: "Active",
          description:
            "Active: Shared, observable, reliable evidence that the exploit is being used in the wild by real attackers; there is credible public reporting.",
        },
      ],
    },
  ];

  return (
    <Box sx={{ m: 1 }}>
      <Grid container spacing={1}>
        {decisionPoints.map((decisionPoint) => (
          <Grid key={decisionPoint.name} item xs={6}>
            <Card variant="outlined" sx={{ p: 3, height: "100%" }}>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  mb: 1,
                }}
              >
                <Typography sx={{ fontWeight: "bold", pr: 0.5 }}>{decisionPoint.name}</Typography>
                <Tooltip title={decisionPoint.description}>
                  <HelpOutlineOutlinedIcon color="action" fontSize="small" />
                </Tooltip>
              </Box>
              <ToggleButtonGroup
                color="primary"
                value={decisionPoint.values[0].name}
                sx={{ mb: 1 }}
              >
                {decisionPoint.values.map((value) => (
                  <ToggleButton key={value.name} value={value.name} disabled>
                    {value.name}
                  </ToggleButton>
                ))}
              </ToggleButtonGroup>
              <Typography variant="body2" color="textSecondary">
                {decisionPoint.values[0].description}
              </Typography>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
