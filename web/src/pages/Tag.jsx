import { Box, Divider, Tab, Tabs, Typography, Chip } from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams, useLocation } from "react-router-dom";

import { PTeamTagLabel } from "../components/PTeamTagLabel.jsx";
import { PTeamTaggedTopics } from "../components/PTeamTaggedTopics";
import { TabPanel } from "../components/TabPanel";
import { TagReferences } from "../components/TagReferences";
import { UUIDTypography } from "../components/UUIDTypography";
import { getPTeamMembers, getPTeamTag, getPTeamServiceTaggedTicketIds } from "../slices/pteam";
import { a11yProps, calcTimestampDiff } from "../utils/func.js";

export function Tag() {
  const [tabValue, setTabValue] = useState(0);
  const [loadMembers, setLoadMembers] = useState(false);
  const [loadPTeamTag, setLoadPTeamTag] = useState(false);
  const [loadTopicList, setLoadTopicList] = useState(false);

  const members = useSelector((state) => state.pteam.members);
  const pteamtags = useSelector((state) => state.pteam.pteamtags);
  const taggedTopics = useSelector((state) => state.pteam.taggedTopics);
  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent
  const pteam = useSelector((state) => state.pteam.pteam);

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { enqueueSnackbar } = useSnackbar();
  const { tagId } = useParams();
  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");
  const serviceId = params.get("serviceId");

  useEffect(() => {
    if (!pteamId || !tagId) return;
    if (!loadTopicList && taggedTopics[tagId] === undefined) {
      setLoadTopicList(true);
    }
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [pteamId, tagId]);

  useEffect(() => {
    if (!loadTopicList || !pteamId || !tagId || !serviceId) return;
    setLoadTopicList(false);
    dispatch(
      getPTeamServiceTaggedTicketIds({ pteamId: pteamId, serviceId: serviceId, tagId: tagId }),
    );
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [loadTopicList, pteamId, tagId, serviceId]);

  useEffect(() => {
    if (!pteamId || !tagId) return;
    if (!loadPTeamTag && pteamtags[tagId] === undefined) {
      setLoadPTeamTag(true);
    }
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [pteamId, tagId]);

  useEffect(() => {
    if (!loadPTeamTag || !pteamId || !tagId) return;
    setLoadPTeamTag(false);
    const onError = (error) => {
      if (error.response?.status === 404) {
        enqueueSnackbar("Specified artifact is not in PTeam monitoring targets.", {
          variant: "error",
        });
        const params = new URLSearchParams();
        params.set("pteamId", pteamId);
        navigate("/?" + params.toString());
      }
    };
    dispatch(getPTeamTag({ pteamId: pteamId, tagId: tagId, onError: onError }));
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [loadPTeamTag, pteamId, tagId]);

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

  if (!allTags || !pteamId || !taggedTopics[tagId] || !pteamtags[tagId]) {
    return <>Now loading...</>;
  }

  const numSolved = taggedTopics[tagId].solved?.topic_ticket_ids?.length ?? 0;
  const numUnsolved = taggedTopics[tagId].unsolved?.topic_ticket_ids?.length ?? 0;

  const pteamtag = pteamtags[tagId];
  const tagDict = allTags.find((tag) => tag.tag_id === tagId);
  const serviceDict = pteam.services.find((service) => service.service_id === serviceId);

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
            <PTeamTagLabel tagId={tagId} />
          </Box>
          <Typography mr={1} mb={1} variant="caption">
            <UUIDTypography sx={{ mr: 2 }}>{tagId}</UUIDTypography>
            {`Updated ${calcTimestampDiff(pteamtag.last_updated_at)}`}
          </Typography>
          <TagReferences references={pteamtag.references} serviceDict={serviceDict} />
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
            pteamtag={pteamtag}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <PTeamTaggedTopics
            pteamId={pteamId}
            tagId={tagId}
            serviceId={serviceDict.service_id}
            isSolved={true}
            pteamtag={pteamtag}
          />
        </TabPanel>
      </Box>
    </>
  );
}
