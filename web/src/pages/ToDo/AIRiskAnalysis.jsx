import ArticleIcon from "@mui/icons-material/Article";
import DirectionsRunIcon from "@mui/icons-material/DirectionsRun";
import DnsIcon from "@mui/icons-material/Dns";
import FindInPageIcon from "@mui/icons-material/FindInPage";
import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import PeopleIcon from "@mui/icons-material/People";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import StorageIcon from "@mui/icons-material/Storage";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Tab,
  Tabs,
  Typography,
  Divider,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { CustomTabPanel } from "../../components/CustomTabPanel";

// --- Data Definitions ---
const threatScenarios = [
  {
    icon: <LocalFireDepartmentIcon />,
    title: "Data Center Fire",
    description:
      "A compromised server's cooling system could be disabled, leading to overheating and a potential fire, causing catastrophic physical damage.",
  },
  {
    icon: <FindInPageIcon />,
    title: "Complete Data Exfiltration",
    description:
      "The vulnerability allows attackers to gain root access, bypassing all security measures to steal sensitive customer and corporate data.",
  },
];

const affectedAssets = [
  {
    icon: <DnsIcon />,
    name: "Production Web Servers (web-prod-01, web-prod-02)",
    impact: "Directly vulnerable. Can be used as an entry point for system takeover.",
  },
  {
    icon: <StorageIcon />,
    name: "Customer Database (customer-db-main)",
    impact: "At risk of data exfiltration or ransom attacks via compromised web servers.",
  },
  {
    icon: <PeopleIcon />,
    name: "End Users & Customers",
    impact: "Personal Identifiable Information (PII) is at high risk of being leaked.",
  },
];

const analysisBasis = {
  dataSources: [
    "NVD (CVE-2021-44228 Entry)",
    "Internal System Architecture Documents (ver 2.1)",
    "Past Incident Reports (INC-2020-115)",
  ],
  reasoning:
    "The AI model identified a direct network path from the vulnerable public-facing servers to the primary customer database. This, combined with historical data from similar Log4j incidents, indicates a high probability of a data breach scenario.",
};

export function AIRiskAnalysis() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  return (
    <>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Risk Analysis: CVE-2021-44228 (Log4Shell)
        </Typography>
        <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
          <Typography variant="body1" color="text.secondary">
            Service: myADV 2023
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Target: ubuntu-20.04
          </Typography>
          <Typography variant="body1" color="text.secondary">
            CVSS: 9.8
          </Typography>
        </Box>
      </Box>

      {/* Main Content */}
      <Paper elevation={3} sx={{ p: 4, borderRadius: 4 }}>
        <Grid container spacing={4}>
          {/* Risk Summary */}
          <Grid item xs={12}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Box>
                <WarningAmberIcon sx={{ fontSize: 40, color: "error.main" }} />
              </Box>
              <Typography variant="h5" component="h2" gutterBottom>
                Risk Summary
              </Typography>
            </Box>
            <List>
              <ListItem>
                <ListItemIcon>
                  <LocalFireDepartmentIcon />
                </ListItemIcon>
                <ListItemText primary="Fire" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <StopCircleIcon />
                </ListItemIcon>
                <ListItemText primary="Service Disruption" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <DirectionsRunIcon />
                </ListItemIcon>
                <ListItemText primary="System Takeover" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <FindInPageIcon />
                </ListItemIcon>
                <ListItemText primary="Data Breach" />
              </ListItem>
            </List>
            {/* A short, concise summary of the risk's most important conclusion by the AI */}
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              High risk of server compromise leading to complete data exfiltration.
            </Typography>
          </Grid>

          {/* Detailed Analysis */}
          <Grid item xs={12}>
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              <Tabs
                value={tabValue}
                variant="scrollable"
                scrollButtons="auto"
                onChange={handleTabChange}
                aria-label="detailed analysis tabs"
              >
                <Tab label="Threat Scenarios" />
                <Tab label="Affected Assets" />
                <Tab label="Analysis Basis" />
              </Tabs>
            </Box>
            <CustomTabPanel value={tabValue} index={0}>
              <Grid container spacing={2}>
                {threatScenarios.map((scenario, index) => (
                  <Grid item xs={12} key={index}>
                    <Card variant="outlined">
                      <CardHeader
                        avatar={<Avatar sx={{ bgcolor: "error.main" }}>{scenario.icon}</Avatar>}
                        title={scenario.title}
                        titleTypographyProps={{ variant: "h6" }}
                      />
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          {scenario.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CustomTabPanel>

            <CustomTabPanel value={tabValue} index={1}>
              <Typography variant="h6" gutterBottom>
                Potentially Affected Assets
              </Typography>
              <List>
                {affectedAssets.map((asset, index) => (
                  <ListItem key={index} divider={index < affectedAssets.length - 1}>
                    <ListItemIcon sx={{ minWidth: 40 }}>{asset.icon}</ListItemIcon>
                    <ListItemText primary={asset.name} secondary={asset.impact} />
                  </ListItem>
                ))}
              </List>
            </CustomTabPanel>

            <CustomTabPanel value={tabValue} index={2}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  Reasoning Logic
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {analysisBasis.reasoning}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" gutterBottom>
                  Data Sources
                </Typography>
                <List dense>
                  {analysisBasis.dataSources.map((source, index) => (
                    <ListItem key={index}>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <ArticleIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={source} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </CustomTabPanel>
          </Grid>
        </Grid>

        {/* Footer: Action Buttons */}
        <Box sx={{ mt: 4, display: "flex", justifyContent: "flex-end", gap: 2 }}>
          <Button variant="outlined">Export Report (PDF)</Button>
          <Button variant="contained">Create Response Ticket</Button>
        </Box>
      </Paper>
    </>
  );
}
