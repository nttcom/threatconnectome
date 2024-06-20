import {
  KeyboardArrowUp as KeyboardArrowUpIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  Recommend as RecommendIcon,
  Warning as WarningIcon,
} from "@mui/icons-material";
import { Badge, Box, Button, Card, Chip, Typography, MenuItem } from "@mui/material";
import { amber, green, grey, orange, red, yellow } from "@mui/material/colors";
import React, { useState } from "react";

import { ActionTypeIcon } from "../components/ActionTypeIcon";
import { threatImpactProps } from "../utils/const";

// Sample Data
const sampleImpactName = "offcycle";

const sampleTitle =
  "npmjs-websocket-extensions: ReDoS vulnerability in Sec-WebSocket-Extensions parser";

const sampleDetail =
  "Memory safety bugs present in Firefox 117, Firefox ESR 115.2, and Thunderbird 115.2.Some of these bugs showed evidence of memory corruption and we presumethat with enough effort some of these could have been exploited to run arbitrary code.This vulnerability affects Firefox  118, Firefox ESR 115.3, and Thunderbird  115.3.";

const sampleCreater = "Tanaka Taro";

const sampleLastupdate = "2024/4/15T11:38:35+09:00";

const sampleTopicId = "fahfia-nkfnaeda-ncjandsjk";

const sampleMispTagLists = [
  {
    id: 1,
    name: "CVE-2020-7662 : xxxx-xxxx-xxxxx",
  },
  {
    id: 2,
    name: "CVE-2020-2573 : xxxx-xxxx-xxxxx",
  },
  {
    id: 3,
    name: "CVE-2020-8474 : xxxx-xxxx-xxxxx",
  },
  {
    id: 4,
    name: "CVE-2020-8493 : xxxx-xxxx-xxxxx",
  },
  {
    id: 5,
    name: "CVE-2020-8928 : xxxx-xxxx-xxxxx",
  },
];

const sampleActionLists = [
  {
    id: 1,
    name: "Update websocket-extensions from version ['>=0, <0.1.4'] to ['0.1.4']",
  },
  {
    id: 2,
    name: "Update websocket-extensions from version ['< 0.1.4'] to ['0.1.4']",
  },
  {
    id: 3,
    name: "Update pygments from version ['>=0, <2.15.0'] to ['2.15.0']",
  },
  {
    id: 4,
    name: "Update pygments from version ['>=0, <2.15.1'] to ['2.15.1']",
  },
];

const sampleArtifactTagLists = [
  {
    id: 1,
    name: "asynckit:npm:",
    affectedVer: "2.1.0-2.5.1",
    patchedVer: "2.6.1",
  },
  {
    id: 2,
    name: "asynckit:npm:",
    affectedVer: "1.2.0-1.4.1",
    patchedVer: "1.5.0",
  },
  {
    id: 3,
    name: "../../../pkg:golang:",
    affectedVer: "1.4.0-2.1.1",
    patchedVer: "2.2.1",
  },
  {
    id: 4,
    name: "python-rundeps:3.9.2:",
    affectedVer: "2.1.0-3.0.1",
    patchedVer: "3.9.2",
  },
];

const baseStyle = threatImpactProps[sampleImpactName].style;

const threatImpactColor = {
  immediate: {
    bgcolor: red[100],
  },
  offcycle: {
    bgcolor: orange[100],
  },
  acceptable: {
    bgcolor: amber[100],
  },
  none: {
    bgcolor: grey[100],
  },
  safe: {
    bgcolor: green[100],
  },
};

const artifactTagMax = 100;

const artifactTagChip = () => {
  if (sampleArtifactTagLists.length < artifactTagMax) {
    return sampleArtifactTagLists.length - 1;
  } else {
    return "99+";
  }
};

export function TopicDetail() {
  const [handleArtifact, setHandleArtifact] = useState(false);

  const handleArtifactOpen = () => setHandleArtifact(!handleArtifact);

  return (
    <>
      <Box>
        <Card
          variant="outlined"
          sx={{ margin: 1, backgroundColor: threatImpactColor[sampleImpactName].bgcolor }}
        >
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Chip
                label={threatImpactProps[sampleImpactName].chipLabel}
                variant="filled"
                sx={{
                  mr: 3,
                  height: 60,
                  fontWeight: "bold",
                  backgroundColor: baseStyle.bgcolor,
                  color: "white",
                }}
              />
              <Typography variant="h5">{sampleTitle}</Typography>
            </Box>
            <Box sx={{ mt: 2, ml: 1 }}>
              <Typography sx={{ color: grey[700] }}>{sampleDetail}</Typography>
            </Box>
          </Box>
        </Card>
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Typography sx={{ fontWeight: "bold" }}>Artifact Tag</Typography>
            <Card
              variant="outlined"
              display="flex"
              flexDirection="row"
              sx={{ margin: 1, padding: 2 }}
            >
              <Typography variant="h5">{sampleArtifactTagLists[0].name}</Typography>
              <Box display="flex" flexDirection="row" justifyContent="center">
                <Box
                  alignItems="center"
                  display="flex"
                  flexDirection="row"
                  justifyContent="center"
                  sx={{ width: "50%" }}
                >
                  <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
                  <Typography sx={{ fontSize: 32 }}>
                    {sampleArtifactTagLists[0].affectedVer}
                  </Typography>
                </Box>
                <Box
                  alignItems="center"
                  display="flex"
                  flexDirection="row"
                  justifyContent="center"
                  sx={{ width: "50%" }}
                >
                  <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
                  <Typography sx={{ fontSize: 32 }}>
                    {sampleArtifactTagLists[0].patchedVer}
                  </Typography>
                </Box>
              </Box>
            </Card>
            {handleArtifact ? (
              <>
                {sampleArtifactTagLists.map((artifactTag, index) => (
                  <>
                    {index !== 0 ? (
                      <Card
                        key={artifactTag.id}
                        variant="outlined"
                        display="flex"
                        flexDirection="row"
                        sx={{ margin: 1, padding: 2 }}
                      >
                        <Typography variant="h5">{artifactTag.name}</Typography>
                        <Box display="flex" flexDirection="row" justifyContent="center">
                          <Box
                            alignItems="center"
                            display="flex"
                            flexDirection="row"
                            justifyContent="center"
                            sx={{ width: "50%" }}
                          >
                            <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
                            <Typography sx={{ fontSize: 32 }}>{artifactTag.affectedVer}</Typography>
                          </Box>
                          <Box
                            alignItems="center"
                            display="flex"
                            flexDirection="row"
                            justifyContent="center"
                            sx={{ width: "50%" }}
                          >
                            <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
                            <Typography sx={{ fontSize: 32 }}>{artifactTag.patchedVer}</Typography>
                          </Box>
                        </Box>
                      </Card>
                    ) : (
                      <></>
                    )}
                  </>
                ))}
              </>
            ) : (
              <></>
            )}
            {sampleArtifactTagLists.length <= 1 ? (
              <></>
            ) : (
              <>
                <Box display="flex" alignItems="center" sx={{ mr: 3 }}>
                  <Box flexGrow={1} />
                  {handleArtifact ? (
                    <Button
                      onClick={handleArtifactOpen}
                      variant="outlined"
                      size="small"
                      sx={{ textTransform: "none", width: 120 }}
                    >
                      <KeyboardArrowUpIcon sx={{ ml: -1 }} />
                      Hide
                    </Button>
                  ) : (
                    <Badge badgeContent={artifactTagChip()} color="primary" sx={{ mt: 1 }}>
                      <Button
                        onClick={handleArtifactOpen}
                        variant="outlined"
                        size="small"
                        sx={{ textTransform: "none", width: 120 }}
                      >
                        <KeyboardArrowDownIcon sx={{ ml: -1 }} />
                        More
                      </Button>
                    </Badge>
                  )}
                  <Box flexGrow={1} />
                </Box>
              </>
            )}
          </Box>
        </Card>
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Typography sx={{ fontWeight: "bold" }}>MISP Tag</Typography>
            </Box>
            {sampleMispTagLists.length === 0 ? (
              <Typography sx={{ margin: 1 }}>No data</Typography>
            ) : (
              <>
                <Box sx={{ mt: 1 }}>
                  {sampleMispTagLists.map((mispTag) => (
                    <Chip
                      key={mispTag.id}
                      label={mispTag.name}
                      size="small"
                      sx={{ m: 0.5, borderRadius: 0.5 }}
                    />
                  ))}
                </Box>
              </>
            )}
          </Box>
        </Card>
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Typography sx={{ fontWeight: "bold" }}>Action</Typography>
            </Box>
            {sampleActionLists.length === 0 ? (
              <Typography sx={{ margin: 1 }}>No data</Typography>
            ) : (
              <>
                <Box>
                  {sampleActionLists.map((actionList) => (
                    <MenuItem
                      key={actionList.id}
                      sx={{
                        alignItems: "center",
                        display: "flex",
                        flexDirection: "row",
                      }}
                    >
                      <ActionTypeIcon actionType="elimination" />
                      <Box display="flex" flexDirection="column">
                        <Typography noWrap variant="body">
                          {actionList.name}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Box>
              </>
            )}
          </Box>
        </Card>
        <Card variant="outlined" sx={{ margin: 1, mb: 3 }}>
          <Box sx={{ margin: 3 }}>
            <Box display="flex" flexDirection="column">
              <Typography sx={{ fontWeight: "bold" }}>Creater</Typography>
              <Typography>{sampleCreater}</Typography>
            </Box>
            <Box display="flex" flexDirection="column" sx={{ mt: 1 }}>
              <Typography sx={{ fontWeight: "bold" }}>Last Updated</Typography>
              <Typography>{sampleLastupdate}</Typography>
            </Box>
            <Box display="flex" flexDirection="column" sx={{ mt: 1 }}>
              <Typography sx={{ fontWeight: "bold" }}>Topic ID</Typography>
              <Typography>{sampleTopicId}</Typography>
            </Box>
          </Box>
        </Card>
      </Box>
    </>
  );
}
