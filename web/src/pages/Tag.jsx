import { Box, Divider, Tab, Tabs, Typography, Chip } from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams, useLocation } from "react-router-dom";

import { PTeamTaggedTopics } from "../components/PTeamTaggedTopics";
import { TabPanel } from "../components/TabPanel";
import { TagReferences } from "../components/TagReferences";
import { UUIDTypography } from "../components/UUIDTypography";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetPTeamQuery, useGetPTeamServiceTaggedTopicIdsQuery } from "../services/tcApi";
import { getDependencies } from "../slices/pteam";
import { a11yProps, errorToString } from "../utils/func.js";

export function Tag() {
  const [tabValue, setTabValue] = useState(0);

  const allTags = useSelector((state) => state.tags.allTags); // dispatched by App
  const serviceDependencies = useSelector((state) => state.pteam.serviceDependencies);

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const { tagId } = useParams();
  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");
  const serviceId = params.get("serviceId");

  const skipByAuth = useSkipUntilAuthTokenIsReady();
  const getPTeamReady = !skipByAuth && pteamId;
  const getTopicIdsReady = getPTeamReady && serviceId && tagId;
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

  const dependencies = serviceDependencies[serviceId];
  const currentTagDependencies = dependencies?.filter((dependency) => dependency.tag_id === tagId);

  useEffect(() => {
    if (!pteam) return; // wait getQuery
    if (!serviceId || !pteam.services.find((service) => service.service_id === serviceId)) {
      const msg = `${serviceId ? "Invalid" : "Missing"} serviceId`;
      enqueueSnackbar(msg, { variant: "error" });
      const params = new URLSearchParams();
      params.set("pteamId", pteamId);
      navigate("/?" + params.toString()); // force jump to Status page
      return;
    }
    if (dependencies === undefined) {
      dispatch(getDependencies({ pteamId: pteamId, serviceId: serviceId }));
      return;
    }
    if (!tagId || !currentTagDependencies?.length > 0) {
      const msg = `${tagId ? "Invalid" : "Missing"} tagId`;
      enqueueSnackbar(msg, { variant: "error" });
      const params = new URLSearchParams();
      params.set("pteamId", pteamId);
      navigate("/?" + params.toString()); // force jump to Status page
      return;
    }
  }, [
    pteam,
    dependencies,
    currentTagDependencies,
    taggedTopics,
    pteamId,
    serviceId,
    tagId,
    dispatch,
    enqueueSnackbar,
    navigate,
  ]);

  if (!getTopicIdsReady) return <></>;
  if (pteamError) return <>{`Cannot get PTeam: ${errorToString(pteamError)}`}</>;
  if (pteamIsLoading) return <>Now loading PTeam...</>;
  if (taggedTopicsError)
    return <>{`Cannot get TaggedTopics: ${errorToString(taggedTopicsError)}`}</>;
  if (taggedTopicsIsLoading) return <>Now loading TaggedTopics...</>;

  if (!allTags || !currentTagDependencies) return <>Now loading...</>;

  const numSolved = taggedTopics.solved?.topic_ids?.length ?? 0;
  const numUnsolved = taggedTopics.unsolved?.topic_ids?.length ?? 0;

  const tagDict = allTags.find((tag) => tag.tag_id === tagId);
  const serviceDict = pteam.services.find((service) => service.service_id === serviceId);
  const references = currentTagDependencies.map((dependency) => ({
    target: dependency.target,
    version: dependency.version,
    service: serviceDict.service_name,
  }));

  const taggedTopicsUnsolved = taggedTopics?.["unsolved"];
  const taggedTopicsSolved = taggedTopics?.["solved"];

  const handleTabChange = (event, value) => setTabValue(value);

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" mt={3} mb={3}>
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
            tagId={tagId}
            service={serviceDict}
            references={references}
            taggedTopics={taggedTopicsUnsolved}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <PTeamTaggedTopics
            pteamId={pteamId}
            tagId={tagId}
            service={serviceDict}
            references={references}
            taggedTopics={taggedTopicsSolved}
          />
        </TabPanel>
      </Box>
    </>
  );
}
