import {
  KeyboardArrowUp as KeyboardArrowUpIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  Recommend as RecommendIcon,
  Warning as WarningIcon,
} from "@mui/icons-material";
import {
  Avatar,
  Badge,
  Box,
  Button,
  Card,
  Chip,
  MenuItem,
  Tooltip,
  Typography,
} from "@mui/material";
import { green, grey, yellow } from "@mui/material/colors";
import React, { useState } from "react";
import { useParams } from "react-router-dom";

import { ActionTypeIcon } from "../../components/ActionTypeIcon";
import { useSkipUntilAuthTokenIsReady } from "../../hooks/auth";
import { useGetTopicActionsQuery, useGetTopicQuery } from "../../services/tcApi";
import { errorToString, cvssProps } from "../../utils/func";

import { TopicSSVCCards } from "./TopicSSVCCards";

const artifactTagChip = (chipNumber) => {
  const artifactTagMax = 99;
  return chipNumber <= artifactTagMax ? chipNumber : `${artifactTagMax}+`;
};

function pickAffectedVersions(topicActions, tagName) {
  const versions = topicActions.reduce(
    (ret, action) => [...ret, ...(action.ext?.vulnerable_versions?.[tagName] ?? [])],
    [],
  );
  if (versions.length > 0) {
    return [...new Set(versions)].sort();
  }
  return ["?"]; // default(fake?) affected version for the case not found
}

export function TopicDetail() {
  const { topicId } = useParams();

  const [showAllArtifacts, setShowAllArtifacts] = useState(false);

  const skip = useSkipUntilAuthTokenIsReady();

  const {
    data: topic,
    error: topicError,
    isLoading: topicIsLoading,
  } = useGetTopicQuery(topicId, { skip });

  const {
    data: topicActions,
    error: topicActionsError,
    isLoading: topicActionsIsLoading,
  } = useGetTopicActionsQuery(topicId, { skip });

  if (skip) return <></>;
  if (topicError) return <>{`Cannot get Topic: ${errorToString(topicError)}`}</>;
  if (topicIsLoading) return <>Now loading Topic...</>;
  if (topicActionsError)
    return <>{`Cannot get topicActions: ${errorToString(topicActionsError)}`}</>;
  if (topicActionsIsLoading) return <>Now loading topicActions...</>;

  const cvssScore =
    topic.cvss_v3_score === undefined || topic.cvss_v3_score === null ? "N/A" : topic.cvss_v3_score;

  const cvss = cvssProps(cvssScore);

  return (
    <>
      <Box>
        <Card variant="outlined" sx={{ margin: 1, backgroundColor: cvss.threatCardBgcolor }}>
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Avatar
                sx={{
                  mr: 3,
                  height: 60,
                  width: 60,
                  fontWeight: "bold",
                  backgroundColor: cvss.cvssBgcolor,
                }}
                variant="rounded"
              >
                {cvssScore === "N/A" ? cvssScore : cvssScore.toFixed(1)}
              </Avatar>
              <Typography variant="h5">{topic.title}</Typography>
            </Box>
            <Box sx={{ mt: 2, ml: 1 }}>
              <Typography sx={{ color: grey[700] }}>{topic.abstract}</Typography>
            </Box>
          </Box>
        </Card>
        {/* Artifact Tag */}
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Typography sx={{ fontWeight: "bold" }}>Artifact Tag</Typography>
            {topic.tags
              .filter((artifactTag, index) => (showAllArtifacts ? true : index === 0))
              .map((artifactTag) => (
                <Card
                  key={artifactTag.tag_id}
                  variant="outlined"
                  display="flex"
                  sx={{ margin: 1, padding: 2 }}
                >
                  <Typography variant="h5">{artifactTag.tag_name}</Typography>
                  <Box display="flex" flexDirection="row" justifyContent="center">
                    {/* left half -- affected versions */}
                    <Box
                      alignItems="flexStart"
                      display="flex"
                      flexDirection="column"
                      sx={{ width: "50%", minWidth: "50%" }}
                    >
                      {pickAffectedVersions(topicActions, artifactTag.tag_name).map(
                        (affectedVersion) => (
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
                        ),
                      )}
                    </Box>
                    {/* right half -- patched versions */}
                    <Box
                      alignItems="center"
                      display="flex"
                      flexDirection="row"
                      sx={{ width: "50%", ml: 2 }}
                    >
                      <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
                      <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                        {"-" /* not yet supported */}
                      </Typography>
                    </Box>
                  </Box>
                </Card>
              ))}
            {/* hide or more button if needed */}
            {topic.tags.length > 1 && (
              <Box display="flex" justifyContent="center" sx={{ mr: 3 }}>
                {showAllArtifacts ? (
                  <Button
                    onClick={() => setShowAllArtifacts(false)}
                    variant="outlined"
                    size="small"
                    sx={{ textTransform: "none", width: 120 }}
                  >
                    <KeyboardArrowUpIcon sx={{ ml: -1 }} />
                    Hide
                  </Button>
                ) : (
                  <Badge
                    badgeContent={artifactTagChip(topic.tags.length - 1)}
                    color="primary"
                    sx={{ mt: 1 }}
                  >
                    <Button
                      onClick={() => setShowAllArtifacts(true)}
                      variant="outlined"
                      size="small"
                      sx={{ textTransform: "none", width: 120 }}
                    >
                      <KeyboardArrowDownIcon sx={{ ml: -1 }} />
                      More
                    </Button>
                  </Badge>
                )}
              </Box>
            )}
          </Box>
        </Card>
        {/* SSVC decision points */}
        <TopicSSVCCards exploitation={topic.exploitation} automatable={topic.automatable} />
        {/* MISP Tag */}
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Typography sx={{ fontWeight: "bold" }}>MISP Tag</Typography>
            </Box>
            {topic.misp_tags.length === 0 ? (
              <Typography sx={{ margin: 1 }}>No data</Typography>
            ) : (
              <>
                <Box sx={{ mt: 1 }}>
                  {topic.misp_tags.map((mispTag) => (
                    <Chip
                      key={mispTag.tag_id}
                      label={mispTag.tag_name}
                      size="small"
                      sx={{ m: 0.5, borderRadius: 0.5 }}
                    />
                  ))}
                </Box>
              </>
            )}
          </Box>
        </Card>
        {/* TopicActions */}
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Typography sx={{ fontWeight: "bold" }}>Action</Typography>
            </Box>
            {topicActions.length === 0 ? (
              <Typography sx={{ margin: 1 }}>No data</Typography>
            ) : (
              <>
                <Box>
                  {topicActions.map((action) => (
                    <MenuItem
                      key={action.action_id}
                      sx={{
                        alignItems: "center",
                        display: "flex",
                        flexDirection: "row",
                      }}
                    >
                      <ActionTypeIcon actionType="elimination" disabled={false} />
                      <Box display="flex" flexDirection="column">
                        <Typography noWrap variant="body">
                          {action.action}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Box>
              </>
            )}
          </Box>
        </Card>
        {/* Other topic info */}
        <Card variant="outlined" sx={{ margin: 1, mb: 3 }}>
          <Box sx={{ margin: 3 }}>
            <Box display="flex" flexDirection="column">
              <Typography sx={{ fontWeight: "bold" }}>Creator</Typography>
              <Typography>{topic.created_by}</Typography>
              {/* TODO: convert to email address? */}
            </Box>
            <Box display="flex" flexDirection="column" sx={{ mt: 1 }}>
              <Typography sx={{ fontWeight: "bold" }}>Last Updated</Typography>
              <Typography>{topic.updated_at}</Typography>
            </Box>
            <Box display="flex" flexDirection="column" sx={{ mt: 1 }}>
              <Typography sx={{ fontWeight: "bold" }}>Topic ID</Typography>
              <Typography>{topic.topic_id}</Typography>
            </Box>
          </Box>
        </Card>
      </Box>
    </>
  );
}
