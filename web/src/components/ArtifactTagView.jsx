import { Recommend as RecommendIcon, Warning as WarningIcon } from "@mui/icons-material";
import { Box, Card, Typography, Tooltip } from "@mui/material";
import { green, yellow } from "@mui/material/colors";
import PropTypes from "prop-types";

import { pickAffectedVersions } from "../utils/topicUtils";

export function ArtifactTagView(props) {
  const { artifactTag, topicActions } = props;

  return (
    <Card key={artifactTag.tag_id} variant="outlined" display="flex" sx={{ m: 1, p: 2 }}>
      {/* Title -- tag name */}
      <Typography variant="h5">{artifactTag.tag_name}</Typography>
      <Box display="flex" flexDirection="row" justifyContent="center">
        {/* left half -- affected versions */}
        <Box
          alignItems="flexStart"
          display="flex"
          flexDirection="column"
          sx={{ width: "50%", minWidth: "50%" }}
        >
          {pickAffectedVersions(topicActions, artifactTag.tag_name).map((affectedVersion) => (
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
          ))}
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
ArtifactTagView.propTypes = {
  artifactTag: PropTypes.object.isRequired,
  topicActions: PropTypes.array.isRequired,
};
