import {
  KeyboardArrowUp as KeyboardArrowUpIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
} from "@mui/icons-material";
import { Avatar, Badge, Box, Button, Card, Chip, MenuItem, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useState } from "react";
import { useParams } from "react-router-dom";

import { ActionTypeIcon } from "../../components/ActionTypeIcon";
import { ArtifactTagView } from "../../components/ArtifactTagView";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetTopicActionsQuery, useGetTopicQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { cvssProps } from "../../utils/const";
import { errorToString, cvssConvertToName } from "../../utils/func";

import { TopicSSVCCards } from "./TopicSSVCCards";

const artifactTagChip = (chipNumber) => {
  const artifactTagMax = 99;
  return chipNumber <= artifactTagMax ? chipNumber : `${artifactTagMax}+`;
};

export function TopicDetail() {
  const { topicId } = useParams();

  const [showAllArtifacts, setShowAllArtifacts] = useState(false);

  const skip = useSkipUntilAuthUserIsReady();
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
  if (topicError) throw new APIError(errorToString(topicError), { api: "getTopic" });
  if (topicIsLoading) return <>Now loading Topic...</>;
  if (topicActionsError)
    throw new APIError(errorToString(topicActionsError), { api: "getTopicActions" });
  if (topicActionsIsLoading) return <>Now loading topicActions...</>;

  const cvssScore =
    topic.cvss_v3_score === undefined || topic.cvss_v3_score === null ? "N/A" : topic.cvss_v3_score;

  const cvss = cvssConvertToName(cvssScore);

  return (
    <>
      <Box>
        <Card
          variant="outlined"
          sx={{ margin: 1, backgroundColor: cvssProps[cvss].threatCardBgcolor }}
        >
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Avatar
                sx={{
                  mr: 3,
                  height: 60,
                  width: 60,
                  fontWeight: "bold",
                  backgroundColor: cvssProps[cvss].cvssBgcolor,
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
                <ArtifactTagView
                  key={artifactTag.tag_id}
                  artifactTag={artifactTag}
                  topicActions={topicActions}
                />
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
        {/* Topic Tag */}
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Typography sx={{ fontWeight: "bold" }}>Topic Tags</Typography>
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
