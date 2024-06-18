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
import {
  getDependencies,
  getPTeam,
  getPTeamMembers,
  getPTeamServiceTaggedTicketIds,
} from "../slices/pteam";
import { getLastUpdatedUncompletedTopicByServiceTag } from "../utils/api.js";
import { a11yProps, calcTimestampDiff } from "../utils/func.js";

export function Tag() {
  const [tabValue, setTabValue] = useState(0);
  const [loadMembers, setLoadMembers] = useState(false);
  const [loadPTeam, setLoadPTeam] = useState(false);
  const [loadDependencies, setLoadDependencies] = useState(false);
  const [loadTopicList, setLoadTopicList] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null);
  const [loadLastUpdatedAt, setLoadLastUpdatedAt] = useState(true);

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const members = useSelector((state) => state.pteam.members);
  const serviceDependencies = useSelector((state) => state.pteam.serviceDependencies);
  const taggedTopics = useSelector((state) => state.pteam.taggedTopics);
  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent
  const pteam = useSelector((state) => state.pteam.pteam);

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { enqueueSnackbar } = useSnackbar();
  const { tagId } = useParams();
  const params = new URLSearchParams(useLocation().search);
  const serviceId = params.get("serviceId");

  const dependencies = serviceDependencies[serviceId];

  useEffect(() => {
    if (!pteamId || !tagId) return;
    if (!loadTopicList && taggedTopics[tagId] === undefined) {
      setLoadTopicList(true);
    }
    if (!loadPTeam && pteam === undefined) {
      setLoadPTeam(true);
    }
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [pteamId, tagId]);

  useEffect(() => {
    if (!pteamId || !loadPTeam) return;
    setLoadPTeam(false);
    dispatch(getPTeam(pteamId));
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [loadPTeam, pteamId]);

  useEffect(() => {
    if (!loadTopicList || !pteamId || !tagId || !serviceId) return;
    setLoadTopicList(false);
    dispatch(
      getPTeamServiceTaggedTicketIds({ pteamId: pteamId, serviceId: serviceId, tagId: tagId }),
    );
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [loadTopicList, pteamId, tagId, serviceId]);

  useEffect(() => {
    if (!pteamId) return;
    if (typeof members === "undefined") {
      setLoadMembers(true);
    }
  }, [pteamId, members]);

  useEffect(() => {
    if (loadMembers) {
      dispatch(getPTeamMembers(pteamId));
    }
  }, [dispatch, loadMembers, pteamId]);

  useEffect(() => {
    if (!pteamId || !serviceId) return;
    if (dependencies === undefined) {
      setLoadDependencies(true);
    }
  }, [pteamId, serviceId, dependencies]);

  useEffect(() => {
    if (loadDependencies) {
      setLoadDependencies(false);
      dispatch(getDependencies({ pteamId: pteamId, serviceId: serviceId }));
    }
  }, [dispatch, loadDependencies, pteamId, serviceId]);

  useEffect(() => {
    if (!pteamId || !serviceId || !tagId || !loadLastUpdatedAt) return;
    async function loadLastUpdatedAt() {
      await getLastUpdatedUncompletedTopicByServiceTag(pteamId, serviceId, tagId)
        .then((response) => {
          const lastUpdatedTopic = response.data;
          setLastUpdatedAt(lastUpdatedTopic.updated_at);
        })
        .catch((error) => {
          setLastUpdatedAt(null);
        })
        .finally(() => {
          setLoadLastUpdatedAt(false);
        });
    }

    loadLastUpdatedAt();
  }, [pteamId, serviceId, tagId, loadLastUpdatedAt]);

  if (!allTags || !pteamId || !pteam || !taggedTopics[tagId]) {
    return <>Now loading...</>;
  }
  if (dependencies === undefined) {
    return <>Now loading Dependencies...</>;
  }

  const numSolved = taggedTopics[tagId].solved?.topic_ticket_ids?.length ?? 0;
  const numUnsolved = taggedTopics[tagId].unsolved?.topic_ticket_ids?.length ?? 0;

  const tagDict = allTags.find((tag) => tag.tag_id === tagId);
  const serviceDict = pteam.services.find((service) => service.service_id === serviceId);
  const references = dependencies
    .filter((dependency) => dependency.tag_id === tagId)
    .map((dependency) => ({
      target: dependency.target,
      version: dependency.version,
      service: serviceDict.service_name,
    }));

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
            {`Updated ${calcTimestampDiff(lastUpdatedAt)}`}
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
            serviceId={serviceDict.service_id}
            isSolved={false}
            references={references}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <PTeamTaggedTopics
            pteamId={pteamId}
            tagId={tagId}
            serviceId={serviceDict.service_id}
            isSolved={true}
            references={references}
          />
        </TabPanel>
      </Box>
    </>
  );
}
