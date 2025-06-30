import { Recommend as RecommendIcon, Warning as WarningIcon } from "@mui/icons-material";
import { Box, Card, Typography, Tooltip } from "@mui/material";
import { green, yellow } from "@mui/material/colors";
import PropTypes from "prop-types";

export function PackageView(props) {
  const { vulnPackage } = props;
  const nameWithEcosystem = `${vulnPackage.affected_name}:${vulnPackage.ecosystem}`;
  const affectedVersions = vulnPackage?.affected_versions ?? [];
  const fixedVersions = vulnPackage?.fixed_versions ?? [];

  return (
    <Card key={vulnPackage.package_id} variant="outlined" display="flex" sx={{ m: 1, p: 2 }}>
      {/* Title -- package name */}
      <Typography variant="h5">{nameWithEcosystem}</Typography>
      <Box display="flex" flexDirection="row" justifyContent="center">
        {/* left half -- affected versions */}
        <Box
          alignItems="flexStart"
          display="flex"
          flexDirection="column"
          sx={{ width: "50%", minWidth: "50%" }}
        >
          {affectedVersions.length > 0 ? (
            affectedVersions.map((affectedVersion) => (
              <Box
                key={affectedVersion}
                alignItems="center"
                display="flex"
                flexDirection="row"
                sx={{ ml: 2 }}
              >
                <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
                <Tooltip title={affectedVersion} placement="right">
                  <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                    {affectedVersion}
                  </Typography>
                </Tooltip>
              </Box>
            ))
          ) : (
            <Box alignItems="center" display="flex" flexDirection="row" sx={{ ml: 2 }}>
              <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
              <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                -
              </Typography>
            </Box>
          )}
        </Box>

        {/* right half -- patched versions */}
        <Box
          alignItems="flexStart"
          display="flex"
          flexDirection="column"
          sx={{ width: "50%", minWidth: "50%" }}
        >
          {fixedVersions.length > 0 ? (
            fixedVersions.map((fixedVersion) => (
              <Box
                key={fixedVersion}
                alignItems="center"
                display="flex"
                flexDirection="row"
                sx={{ ml: 2 }}
              >
                <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
                <Tooltip title={fixedVersion} placement="right">
                  <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                    {fixedVersion}
                  </Typography>
                </Tooltip>
              </Box>
            ))
          ) : (
            <Box alignItems="center" display="flex" flexDirection="row" sx={{ ml: 2 }}>
              <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
              <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                -
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Card>
  );
}

PackageView.propTypes = {
  vulnPackage: PropTypes.object.isRequired,
};
