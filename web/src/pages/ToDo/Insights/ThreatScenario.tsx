import { Avatar, Card, CardContent, CardHeader, Grid, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import type { ThreatScenario as ThreatScenarioType } from "../../../../types/types.gen";
import { impactCategoryIcons } from "./insightConst";

type ThreatScenarioProps = {
  threatScenarios: ThreatScenarioType[];
};

export function ThreatScenario(props: ThreatScenarioProps) {
  const { threatScenarios } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "Insights.ThreatScenario" });

  if (!threatScenarios || threatScenarios.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        {t("noScenarios")}
      </Typography>
    );
  }

  return (
    <>
      <Grid container spacing={2} sx={{ flexDirection: "column" }}>
        {threatScenarios.map((scenario, index) => {
          const ImpactCategoryIcon = impactCategoryIcons[scenario.impact_category]?.icon;
          return (
            <Grid size={12} key={index}>
              <Card variant="outlined">
                <CardHeader
                  avatar={
                    <Avatar
                      sx={{
                        bgcolor: "error.main",
                        width: { xs: 32, md: 40 },
                        height: { xs: 32, md: 40 },
                      }}
                    >
                      {ImpactCategoryIcon ? (
                        <ImpactCategoryIcon sx={{ fontSize: { xs: "1rem", md: "1.25rem" } }} />
                      ) : null}
                    </Avatar>
                  }
                  title={scenario.title}
                  slotProps={{
                    title: {
                      variant: "h6",
                      sx: {
                        fontSize: { xs: "1rem", md: "1.25rem" },
                        whiteSpace: "normal",
                        overflowWrap: "break-word",
                      },
                    },
                  }}
                />
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    {scenario.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </>
  );
}
