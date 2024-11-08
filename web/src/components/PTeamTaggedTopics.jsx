import { Box, List, ListItem, MenuItem, Pagination, Select, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { PTeamStatusMenu } from "../components/PTeamStatusMenu";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetPTeamMembersQuery, useGetTagsQuery } from "../services/tcApi";
import { sortedSSVCPriorities } from "../utils/const";
import { errorToString } from "../utils/func";

import { SSVCPriorityCountChip } from "./SSVCPriorityCountChip";
import { TopicCard } from "./TopicCard";

export function PTeamTaggedTopics(props) {
  const { pteamId, tagId, service, references, taggedTopics } = props;

  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const skip = useSkipUntilAuthTokenIsReady() || !pteamId;
  const {
    data: allTags,
    error: allTagsError,
    isLoading: allTagsIsLoading,
  } = useGetTagsQuery(undefined, { skip });
  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetPTeamMembersQuery(pteamId, { skip });

  if (skip) return <></>;
  if (allTagsError) return <>{`Cannot get allTags: ${errorToString(allTagsError)}`}</>;
  if (allTagsIsLoading) return <>Now loading allTags...</>;
  if (membersError) return <>{`Cannot get PTeamMembers: ${errorToString(membersError)}`}</>;
  if (membersIsLoading) return <>Now loading PTeamMembers...</>;

  if (taggedTopics === undefined) {
    return <>Loading...</>;
  }

  const targetTopicIds = taggedTopics.topic_ids.slice(perPage * (page - 1), perPage * page);
  const presetTagId = tagId;
  const presetParentTagId = allTags.find((tag) => tag.tag_id === tagId)?.parent_id;

  const paginationRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
      <Pagination
        shape="rounded"
        page={page}
        count={Math.ceil(taggedTopics.topic_ids.length / perPage)}
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
        {sortedSSVCPriorities.map((ssvcPriority) => (
          <SSVCPriorityCountChip
            key={ssvcPriority}
            ssvcPriority={ssvcPriority}
            count={taggedTopics.ssvc_priority_count[ssvcPriority]}
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
              service={service}
              references={references}
              members={members}
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
  service: PropTypes.object.isRequired,
  references: PropTypes.array.isRequired,
  taggedTopics: PropTypes.object.isRequired,
};
