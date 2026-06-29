import SmartToyOutlinedIcon from "@mui/icons-material/SmartToyOutlined";
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
import type { SyntheticEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import type {
  InsightResponse,
  ThreatScenario as ThreatScenarioType,
} from "../../../../types/types.gen";
import { CustomTabPanel } from "../../../components/CustomTabPanel";

import { AffectedObject } from "./AffectedObject";
import { InsightReference } from "./InsightReference";
import { ThreatScenario } from "./ThreatScenario";
import { impactCategoryIcons } from "./insightConst";

type RiskAnalysisViewProps = {
  insight: InsightResponse;
  serviceName: string;
  ecosystem: string;
  cveId: string;
  cvss: string;
};

export function RiskAnalysisView(props: RiskAnalysisViewProps) {
  const { insight, serviceName, ecosystem, cveId, cvss } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "Insights.RiskAnalysisView" });

  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_event: SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  const threatScenarios = insight.threat_scenarios ?? [];
  const affectedObjects = insight.affected_objects ?? [];
  const insightReferences = insight.insight_references ?? [];

  const uniqueThreatScenarios = threatScenarios.filter(
    (scenario, index, self) =>
      index === self.findIndex((s) => s.impact_category === scenario.impact_category),
  );

  const isIconValid = (scenario: ThreatScenarioType) =>
    Boolean(impactCategoryIcons[scenario.impact_category]?.icon);
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
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontSize: { xs: 30, md: 35 } }}>
          {t("title", { cveId })}
        </Typography>
        <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
          <Typography variant="body1" color="text.secondary">
            {t("service", { serviceName })}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {t("ecosystem", { ecosystem })}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {t("cvss", { cvss })}
          </Typography>
        </Box>
      </Box>

      {/* Main Content */}
      <Paper elevation={3} sx={{ p: { xs: 2, sm: 3, md: 4 }, borderRadius: 4 }}>
        <Grid container spacing={4}>
          {/* Risk Summary */}
          <Grid size={12}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Box>
                <WarningAmberIcon sx={{ fontSize: 40, color: "error.main" }} />
              </Box>
              <Typography variant="h5" component="h2" gutterBottom>
                {t("riskSummary")}
              </Typography>
            </Box>

            {/* Disclaimer for AI-generated content */}
            <Paper
              variant="outlined"
              sx={{
                p: 1.5,
                mb: 2,
                display: "flex",
                alignItems: "center",
                gap: 1.5,
                backgroundColor: "action.hover",
                borderRadius: 2,
                borderColor: "divider",
              }}
            >
              <SmartToyOutlinedIcon sx={{ color: "primary.main" }} />
              <Typography variant="body2" color="text.secondary">
                <Typography component="span" variant="body2" sx={{ fontWeight: "bold" }}>
                  {t("aiGeneratedLabel")}
                </Typography>
                {t("aiGeneratedDisclaimer")}
              </Typography>
            </Paper>

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
          <Grid size={12}>
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              <Tabs
                value={tabValue}
                variant="scrollable"
                scrollButtons
                allowScrollButtonsMobile
                onChange={handleTabChange}
                aria-label="detailed analysis tabs"
              >
                <Tab label={t("tabThreatScenarios")} />
                <Tab label={t("tabAffectedAssets")} />
                <Tab label={t("tabAnalysisBasis")} />
              </Tabs>
            </Box>
            <CustomTabPanel value={tabValue} index={0}>
              <ThreatScenario threatScenarios={threatScenarios} />
            </CustomTabPanel>

            <CustomTabPanel value={tabValue} index={1}>
              <AffectedObject affectedObjects={affectedObjects} />
            </CustomTabPanel>

            <CustomTabPanel value={tabValue} index={2}>
              <InsightReference
                dataProcessingStrategy={insight.data_processing_strategy}
                insightReferences={insightReferences}
              />
            </CustomTabPanel>
          </Grid>
        </Grid>

        {/* Footer: Action Buttons */}
        <Box
          sx={{
            mt: 4,
            display: "flex",
            justifyContent: "flex-end",
            gap: 2,
            flexDirection: { xs: "column", sm: "row" },
          }}
        >
          <Button variant="outlined" disabled>
            {t("exportPdf")}
          </Button>
          <Button variant="contained" disabled>
            {t("createTicket")}
          </Button>
        </Box>
      </Paper>
    </>
  );
}
