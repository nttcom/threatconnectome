import { Box, Divider, Tab, Tabs, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";

import { PTeamTagLabel } from "../components/PTeamTagLabel.jsx";
import { PTeamTaggedTopics } from "../components/PTeamTaggedTopics";
import { TabPanel } from "../components/TabPanel";
import { TagReferences } from "../components/TagReferences";
import { UUIDTypography } from "../components/UUIDTypography";
import {
  getPTeamMembers,
  getPTeamTag,
  getPTeamSolvedTaggedTopicIds,
  getPTeamUnsolvedTaggedTopicIds,
} from "../slices/pteam";
import { a11yProps, calcTimestampDiff } from "../utils/func.js";

export function Tag() {
  const [tabValue, setTabValue] = useState(0);
  const [loadMembers, setLoadMembers] = useState(false);
  const [loadPTeamTag, setLoadPTeamTag] = useState(false);
  const [loadTopicList, setLoadTopicList] = useState(false);

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const members = useSelector((state) => state.pteam.members);
  const pteamtags = useSelector((state) => state.pteam.pteamtags);
  const taggedTopics = useSelector((state) => state.pteam.taggedTopics);
  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent

  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { enqueueSnackbar } = useSnackbar();
  const { tagId } = useParams();

  useEffect(() => {
    if (!pteamId || !tagId) return;
    if (!loadTopicList && taggedTopics[tagId] === undefined) {
      setLoadTopicList(true);
    }
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [pteamId, tagId]);

  useEffect(() => {
    if (!loadTopicList || !pteamId || !tagId) return;
    setLoadTopicList(false);
    dispatch(getPTeamSolvedTaggedTopicIds({ pteamId: pteamId, tagId: tagId }));
    dispatch(getPTeamUnsolvedTaggedTopicIds({ pteamId: pteamId, tagId: tagId }));
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [loadTopicList, pteamId, tagId]);

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

  const numSolved = taggedTopics[tagId].solved?.topic_ids?.length ?? 0;
  const numUnsolved = taggedTopics[tagId].unsolved?.topic_ids?.length ?? 0;
  const pteamtag = pteamtags[tagId];
  const tagDict = allTags.find((tag) => tag.tag_id === tagId);

  const handleTabChange = (event, value) => setTabValue(value);

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" mt={3} mb={3}>
        <Box display="flex" flexDirection="column" flexGrow={1}>
          <Box display="flex" alignItems="center">
            <Typography variant="h4" sx={{ fontWeight: 900 }}>
              {tagDict.tag_name}
            </Typography>
            <PTeamTagLabel tagId={tagId} />
          </Box>
          <UUIDTypography>{tagId}</UUIDTypography>
          <Typography mt={1} mr={1} mb={1} variant="caption">
            {`Updated ${calcTimestampDiff(pteamtag.last_updated_at)}`}
          </Typography>
          <TagReferences references={pteamtag.references} />
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
          <PTeamTaggedTopics pteamId={pteamId} tagId={tagId} isSolved={false} pteamtag={pteamtag} />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <PTeamTaggedTopics pteamId={pteamId} tagId={tagId} isSolved={true} pteamtag={pteamtag} />
        </TabPanel>
      </Box>
    </>
  );
}
