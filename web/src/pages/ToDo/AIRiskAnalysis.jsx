import DirectionsRunIcon from "@mui/icons-material/DirectionsRun";
import FindInPageIcon from "@mui/icons-material/FindInPage";
import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { CustomTabPanel } from "../../components/CustomTabPanel";

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

export function AIRiskAnalysis() {
  const [tabValue, setTabValue] = useState(0);

  const handleAITabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  return (
    <>
      {/* --- ヘッダー部分 --- */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Risk Analysis: CVE-2021-4228 (Log4Shell)
        </Typography>
        <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
          <Typography variant="body1" color="text.secondary">
            Service: myADV 2023
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Target: ubuntu-20.04
          </Typography>
          <Chip label="Critical 9.8" color="error" variant="filled" />
        </Box>
      </Box>

      {/* --- メインコンテンツ --- */}
      <Paper elevation={3} sx={{ p: 4, borderRadius: 4 }}>
        <Grid container spacing={4}>
          {/* --- 左側: リスクサマリー --- */}
          <Grid item xs={12}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Box>
                <WarningAmberIcon sx={{ fontSize: 40, color: "error.main" }} />
              </Box>
              <Typography variant="h5" component="h2" gutterBottom>
                Risk Summary
              </Typography>
            </Box>
            <Box sx={{ textAlign: "center", my: 3 }}>
              <WarningAmberIcon sx={{ fontSize: 60, color: "error.main" }} />
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
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              High risk of server compromise leading to complete data exfiltration.
            </Typography>
          </Grid>

          {/* --- 右側: 詳細分析 --- */}
          <Grid item xs={12}>
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              <Tabs
                value={tabValue}
                variant="scrollable"
                scrollButtons="auto"
                onChange={handleAITabChange}
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
              <Typography>Here are the assets that would be affected.</Typography>
            </CustomTabPanel>

            <CustomTabPanel value={tabValue} index={2}>
              <Typography>
                This analysis is based on past similar incidents and system architecture.
              </Typography>
            </CustomTabPanel>
          </Grid>
        </Grid>

        {/* --- フッター: アクションボタン --- */}
        <Box sx={{ mt: 4, display: "flex", justifyContent: "flex-end", gap: 2 }}>
          <Button variant="outlined">Export Report (PDF)</Button>
          <Button variant="contained">Create Response Ticket</Button>
        </Box>
      </Paper>
    </>
  );
}

AIRiskAnalysis.propTypes = {
  tabValue: PropTypes.number.isRequired,
  handleAITabChange: PropTypes.func.isRequired,
  threatScenarios: PropTypes.arrayOf(
    PropTypes.shape({
      icon: PropTypes.element.isRequired,
      title: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
    }),
  ).isRequired,
};
