import { Box, List, ListItem, MenuItem, Pagination, Select, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetPTeamMembersQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { sortedSSVCPriorities } from "../../utils/const";
import { errorToString } from "../../utils/func";

import { SSVCPriorityCountChip } from "./SSVCPriorityCountChip";
import { TopicCard } from "./TopicCard";

export function PTeamTaggedTopics(props) {
  const { pteamId, service, references, taggedTopics } = props;

  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const skip = useSkipUntilAuthUserIsReady() || !pteamId;

  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetPTeamMembersQuery(pteamId, { skip });

  if (skip) return <></>;
  if (membersError) throw new APIError(errorToString(membersError), { api: "getPTeamMembers" });
  if (membersIsLoading) return <>Now loading PTeamMembers...</>;

  if (taggedTopics === undefined) {
    return <>Loading...</>;
  }

  const targetTopicIds = taggedTopics.topic_ids.slice(perPage * (page - 1), perPage * page);

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
      </Box>
      {paginationRow}
      <List sx={{ p: 0 }}>
        {targetTopicIds.map((topicId) => (
          <ListItem key={topicId} sx={{ minHeight: "250px", p: 0 }}>
            <TopicCard
              key={topicId}
              pteamId={pteamId}
              topicId={topicId}
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
  service: PropTypes.object.isRequired,
  references: PropTypes.array.isRequired,
  taggedTopics: PropTypes.object.isRequired,
};
