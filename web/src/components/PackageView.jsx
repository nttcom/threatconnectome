import { Recommend as RecommendIcon, Warning as WarningIcon } from "@mui/icons-material";
import { Box, Card, Typography, Tooltip, Grid } from "@mui/material";
import { green, yellow } from "@mui/material/colors";
import PropTypes from "prop-types";

export function PackageView(props) {
  const { vulnPackage } = props;
  const nameWithEcosystem = `${vulnPackage.affected_name}:${vulnPackage.ecosystem}`;
  const affectedVersions = vulnPackage?.affected_versions ?? [];
  const fixedVersions = vulnPackage?.fixed_versions ?? [];

  return (
    <Card
      key={vulnPackage.affected_name + vulnPackage.ecosystem}
      variant="outlined"
      sx={{ m: 1, p: 2 }}
    >
      {/* Title -- package name */}
      <Typography variant="h5">{nameWithEcosystem}</Typography>
      <Grid container>
        {/* affected versions */}
        <Grid item xs={12} md={6} sx={{ display: "flex", alignItems: "center" }}>
          {affectedVersions.length > 0 ? (
            affectedVersions.map((affectedVersion) => (
              <Box
                key={affectedVersion}
                sx={{ display: "flex", alignItems: "center", minWidth: 0 }}
              >
                <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
                <Tooltip title={affectedVersion} placement="right">
                  <Typography
                    noWrap
                    sx={{
                      fontSize: 32,
                      mx: 2,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      display: "block",
                    }}
                  >
                    {affectedVersion}
                  </Typography>
                </Tooltip>
              </Box>
            ))
          ) : (
            <Box sx={{ display: "flex", alignItems: "center", ml: 2 }}>
              <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
              <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                -
              </Typography>
            </Box>
          )}
        </Grid>
        {/* patched versions */}
        <Grid item xs={12} md={6} sx={{ display: "flex", alignItems: "center" }}>
          {fixedVersions.length > 0 ? (
            fixedVersions.map((fixedVersion) => (
              <Box key={fixedVersion} sx={{ display: "flex", alignItems: "center" }}>
                <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
                <Tooltip title={fixedVersion} placement="right">
                  <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                    {fixedVersion}
                  </Typography>
                </Tooltip>
              </Box>
            ))
          ) : (
            <Box alignItems="center" display="flex" flexDirection="row">
              <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
              <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                -
              </Typography>
            </Box>
          )}
        </Grid>
      </Grid>
    </Card>
  );
}

PackageView.propTypes = {
  vulnPackage: PropTypes.object.isRequired,
};
