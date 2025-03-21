import { Box, Divider, Tab, Tabs, Typography, Chip } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useState } from "react";
import { useParams, useLocation } from "react-router-dom";

import { TabPanel } from "../../components/TabPanel";
import { UUIDTypography } from "../../components/UUIDTypography";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import {
  useGetPTeamQuery,
  useGetPTeamServiceTaggedTopicIdsQuery,
  useGetTagsQuery,
  useGetDependenciesQuery,
} from "../../services/tcApi";
import { APIError } from "../../utils/APIError.js";
import { noPTeamMessage } from "../../utils/const";
import { a11yProps, errorToString } from "../../utils/func.js";

import { CodeBlock } from "./CodeBlock.jsx";
import { PTeamTaggedTopics } from "./PTeamTaggedTopics.jsx";
import { TagReferences } from "./TagReferences.jsx";

export function Tag() {
  const [tabValue, setTabValue] = useState(0);

  const skipByAuth = useSkipUntilAuthUserIsReady();
  const {
    data: allTags,
    error: allTagsError,
    isLoading: allTagsIsLoading,
  } = useGetTagsQuery(undefined, { skipByAuth });

  const { tagId } = useParams();
  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");
  const serviceId = params.get("serviceId");
  const getDependenciesReady = !skipByAuth && pteamId && serviceId;
  const getPTeamReady = !skipByAuth && pteamId;
  const getTopicIdsReady = getPTeamReady && serviceId && tagId;

  const {
    data: serviceDependencies,
    error: serviceDependenciesError,
    isLoading: serviceDependenciesIsLoading,
  } = useGetDependenciesQuery({ pteamId, serviceId }, { skip: !getDependenciesReady });
  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, { skip: !getPTeamReady });
  const {
    data: taggedTopics,
    error: taggedTopicsError,
    isLoading: taggedTopicsIsLoading,
  } = useGetPTeamServiceTaggedTopicIdsQuery(
    { pteamId, serviceId, tagId },
    { skip: !getTopicIdsReady },
  );

  const currentTagDependencies = (serviceDependencies ?? []).filter(
    (dependency) => dependency.tag_id === tagId,
  );

  if (!pteamId) return <>{noPTeamMessage}</>;
  if (!getTopicIdsReady) return <></>;
  if (allTagsError) throw new APIError(errorToString(allTagsError), { api: "getTags" });
  if (allTagsIsLoading) return <>Now loading allTags...</>;
  if (pteamError) throw new APIError(errorToString(pteamError), { api: "getPTeam" });
  if (pteamIsLoading) return <>Now loading Team...</>;
  if (serviceDependenciesError)
    throw new APIError(errorToString(serviceDependenciesError), { api: "getDependencies" });
  if (serviceDependenciesIsLoading) return <>Now loading serviceDependencies...</>;
  if (taggedTopicsError)
    throw new APIError(errorToString(taggedTopicsError), { api: "getPTeamServiceTaggedTopicIds" });
  if (taggedTopicsIsLoading) return <>Now loading TaggedTopics...</>;

  const numSolved = taggedTopics.solved?.topic_ids?.length ?? 0;
  const numUnsolved = taggedTopics.unsolved?.topic_ids?.length ?? 0;

  const tagDict = allTags.find((tag) => tag.tag_id === tagId);
  const serviceDict = pteam.services.find((service) => service.service_id === serviceId);
  const references = currentTagDependencies.map((dependency) => ({
    dependencyId: dependency.dependency_id,
    target: dependency.target,
    version: dependency.version,
    service: serviceDict.service_name,
  }));

  const taggedTopicsUnsolved = taggedTopics?.["unsolved"];
  const taggedTopicsSolved = taggedTopics?.["solved"];

  const handleTabChange = (event, value) => setTabValue(value);

  // CodeBlock is not implemented
  const visibleCodeBlock = false;

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" mt={3} mb={2}>
        <Box display="flex" flexDirection="column" flexGrow={1}>
          <Box>
            <Chip
              label={serviceDict.service_name}
              variant="outlined"
              sx={{
                borderRadius: "2px",
                border: `1px solid ${grey[700]}`,
                borderLeft: `5px solid ${grey[700]}`,
                mr: 1,
                mb: 1,
              }}
            />
          </Box>
          <Box display="flex" alignItems="center" sx={{ mb: 1 }}>
            <Typography variant="h4" sx={{ fontWeight: 900 }}>
              {tagDict.tag_name}
            </Typography>
          </Box>
          <Typography mr={1} mb={1} variant="caption">
            <UUIDTypography sx={{ mr: 2 }}>{tagId}</UUIDTypography>
          </Typography>
          <TagReferences references={references} serviceDict={serviceDict} />
        </Box>
      </Box>
      <CodeBlock visible={visibleCodeBlock} />
      <Divider />
      <Box sx={{ width: "100%" }}>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="pteam_tagged_topic_tabs">
            <Tab label={`UNSOLVED TOPICS (${numUnsolved})`} {...a11yProps(0)} />
            <Tab label={`SOLVED TOPICS (${numSolved})`} {...a11yProps(1)} />
          </Tabs>
        </Box>
        <TabPanel value={tabValue} index={0}>
          <PTeamTaggedTopics
            pteamId={pteamId}
            service={serviceDict}
            tagId={tagId}
            references={references}
            taggedTopics={taggedTopicsUnsolved}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <PTeamTaggedTopics
            pteamId={pteamId}
            service={serviceDict}
            tagId={tagId}
            references={references}
            taggedTopics={taggedTopicsSolved}
          />
        </TabPanel>
      </Box>
    </>
  );
}
