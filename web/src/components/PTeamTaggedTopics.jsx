import { Box, List, ListItem, MenuItem, Pagination, Select, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useSelector } from "react-redux";

import { PTeamStatusMenu } from "../components/PTeamStatusMenu";

import { ThreatImpactCountChip } from "./ThreatImpactCountChip";
import { TopicCard } from "./TopicCard";

export function PTeamTaggedTopics(props) {
  const { pteamId, tagId, isSolved, pteamtag } = props;

  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const taggedTopics = useSelector((state) => state.pteam.taggedTopics); // dispatched by parent
  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent

  const targets = isSolved ? taggedTopics?.[tagId]?.solved : taggedTopics?.[tagId]?.unsolved;

  if (targets === undefined || !allTags) {
    return <>Loading...</>;
  }

  const targetTopicIds = targets.topic_ids.slice(perPage * (page - 1), perPage * page);
  const presetTagId = tagId;
  const presetParentTagId = allTags.find((tag) => tag.tag_id === tagId)?.parent_id;

  const paginationRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
      <Pagination
        shape="rounded"
        page={page}
        count={Math.ceil(targets.topic_ids.length / perPage)}
        onChange={(event, value) => setPage(value)}
      />
      <Select
        size="small"
        variant="standard"
        value={perPage}
        onChange={(event) => {
          setPerPage(event.target.value);
          setPage(1);
        }}
      >
        {[10, 20, 50, 100].map((num) => (
          <MenuItem key={num} value={num} sx={{ justifyContent: "flex-end" }}>
            <Typography variant="body2" sx={{ mt: 0.3 }}>
              {num} Rows
            </Typography>
          </MenuItem>
        ))}
      </Select>
      <Box flexGrow={1} />
    </Box>
  );

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" my={2}>
        {["1", "2", "3", "4"].map((impact) => (
          <ThreatImpactCountChip
            key={impact}
            threatImpact={impact}
            count={targets.threat_impact_count[impact]}
            outerSx={{ mr: "10px" }}
          />
        ))}
        <Box flexGrow={1} />
        <PTeamStatusMenu presetTagId={presetTagId} presetParentTagId={presetParentTagId} />
      </Box>
      {paginationRow}
      <List sx={{ p: 0 }}>
        {targetTopicIds.map((topicId) => (
          <ListItem key={topicId} sx={{ minHeight: "250px", p: 0 }}>
            <TopicCard
              key={topicId}
              pteamId={pteamId}
              topicId={topicId}
              currentTagId={tagId}
              pteamtag={pteamtag}
            />
          </ListItem>
        ))}
      </List>
      {targetTopicIds.length > 3 && paginationRow}
    </>
  );
}
PTeamTaggedTopics.propTypes = {
  pteamId: PropTypes.string.isRequired,
  tagId: PropTypes.string.isRequired,
  isSolved: PropTypes.bool.isRequired,
  pteamtag: PropTypes.object.isRequired,
};
