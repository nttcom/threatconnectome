import { Avatar, Card, CardContent, CardHeader, Grid, Typography } from "@mui/material";
import PropTypes from "prop-types";

import { impactCategoryIcons } from "./insightConst.js";

export function ThreatScenario(props) {
  const { threatScenarios } = props;

  if (!threatScenarios || threatScenarios.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No threat scenarios available.
      </Typography>
    );
  }

  return (
    <>
      <Grid container spacing={2} sx={{ flexDirection: "column" }}>
        {threatScenarios.map((scenario, index) => {
          const ImpactCategoryIcon = impactCategoryIcons[scenario.impact_category].icon;
          return (
            <Grid item xs={12} key={index}>
              <Card variant="outlined">
                <CardHeader
                  avatar={
                    <Avatar sx={{ bgcolor: "error.main" }}>
                      <ImpactCategoryIcon />
                    </Avatar>
                  }
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
          );
        })}
      </Grid>
    </>
  );
}

ThreatScenario.propTypes = {
  threatScenarios: PropTypes.arrayOf(PropTypes.object).isRequired,
};
