import { Recommend as RecommendIcon, Warning as WarningIcon } from "@mui/icons-material";
import { Box, Card, Typography, Tooltip } from "@mui/material";
import { green, yellow } from "@mui/material/colors";
import PropTypes from "prop-types";

export function PackageView(props) {
  const { packageInfo, affect } = props;
  const nameWithEcosystem = `${packageInfo.name}:${packageInfo.ecosystem}`;
  const affectedVersions = affect?.affected_versions ?? [];

  return (
    <Card key={packageInfo.package_id} variant="outlined" display="flex" sx={{ m: 1, p: 2 }}>
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
          {affectedVersions.length === 0 ? (
            <Typography sx={{ fontSize: 20, color: yellow[900], ml: 2 }}>-</Typography>
          ) : (
            affectedVersions.map((ver, idx) => (
              <Box key={ver} alignItems="center" display="flex" flexDirection="row" sx={{ ml: 2 }}>
                <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
                <Tooltip title={ver} placement="right">
                  <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                    {ver}
                  </Typography>
                </Tooltip>
              </Box>
            ))
          )}
        </Box>
        {/* right half -- patched versions */}
        <Box alignItems="center" display="flex" flexDirection="row" sx={{ width: "50%", ml: 2 }}>
          <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
          <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
            {"-" /* not yet supported */}
          </Typography>
        </Box>
      </Box>
    </Card>
  );
}
PackageView.propTypes = {
  packageInfo: PropTypes.object.isRequired,
  affect: PropTypes.object.isRequired,
};
