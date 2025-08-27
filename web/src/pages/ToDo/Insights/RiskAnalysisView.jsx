import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import {
  Box,
  Button,
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

import { CustomTabPanel } from "../../../components/CustomTabPanel.jsx";

import { AffectedObject } from "./AffectedObject.jsx";
import { InsightReference } from "./InsightReference.jsx";
import { ThreatScenario } from "./ThreatScenario.jsx";
import { impactCategoryIcons } from "./insightConst.js";

export function RiskAnalysisView(props) {
  const { insight, serviceName, ecosystem, cveId, cvss } = props;

  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  const uniqueThreatScenarios = insight.threat_scenarios.filter(
    (scenario, index, self) =>
      index === self.findIndex((s) => s.impact_category === scenario.impact_category),
  );

  const isIconValid = (scenario) => Boolean(impactCategoryIcons[scenario.impact_category]?.icon);
  if (!uniqueThreatScenarios.every((scenario) => isIconValid(scenario))) {
    return (
      <Typography variant="body2" color="text.secondary">
        No icon found for the specified impact category.
      </Typography>
    );
  }

  return (
    <>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Risk Analysis: {cveId}
        </Typography>
        <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
          <Typography variant="body1" color="text.secondary">
            Service: {serviceName}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Target: {ecosystem}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            CVSS: {cvss}
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
              {uniqueThreatScenarios.map((scenario, index) => {
                const RiskIcon = impactCategoryIcons[scenario.impact_category].icon;
                const riskText = impactCategoryIcons[scenario.impact_category].text;
                return (
                  <ListItem key={index}>
                    <ListItemIcon>{RiskIcon ? <RiskIcon /> : null}</ListItemIcon>
                    <ListItemText primary={riskText} />
                  </ListItem>
                );
              })}
            </List>
            {/* A short, concise summary of the risk's most important conclusion by the AI */}
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              {insight.description}
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
              <ThreatScenario threatScenarios={insight.threat_scenarios} />
            </CustomTabPanel>

            <CustomTabPanel value={tabValue} index={1}>
              <AffectedObject affectedObjects={insight.affected_objects} />
            </CustomTabPanel>

            <CustomTabPanel value={tabValue} index={2}>
              <InsightReference
                dataProcessingStrategy={insight.data_processing_strategy}
                insightReferences={insight.insight_references}
              />
            </CustomTabPanel>
          </Grid>
        </Grid>

        {/* Footer: Action Buttons */}
        <Box sx={{ mt: 4, display: "flex", justifyContent: "flex-end", gap: 2 }}>
          <Button variant="outlined" disabled>
            Export Report (PDF)
          </Button>
          <Button variant="contained" disabled>
            Create Response Ticket
          </Button>
        </Box>
      </Paper>
    </>
  );
}

RiskAnalysisView.propTypes = {
  insight: PropTypes.object.isRequired,
  serviceName: PropTypes.string.isRequired,
  ecosystem: PropTypes.string.isRequired,
  cveId: PropTypes.string.isRequired,
  cvss: PropTypes.string.isRequired,
};
