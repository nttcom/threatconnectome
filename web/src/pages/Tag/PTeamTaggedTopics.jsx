import { Box } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { TopicTable } from "../../components/TopicTable";
import { useSkipUntilAuthTokenIsReady } from "../../hooks/auth";
import { useGetPTeamMembersQuery } from "../../services/tcApi";
import { sortedSSVCPriorities } from "../../utils/const";
import { errorToString } from "../../utils/func";

import { SSVCPriorityCountChip } from "./SSVCPriorityCountChip";

export function PTeamTaggedTopics(props) {
  const { pteamId, service, references, taggedTopics } = props;

  const skip = useSkipUntilAuthTokenIsReady() || !pteamId;

  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetPTeamMembersQuery(pteamId, { skip });

  if (skip) return <></>;
  if (membersError) return <>{`Cannot get PTeamMembers: ${errorToString(membersError)}`}</>;
  if (membersIsLoading) return <>Now loading PTeamMembers...</>;

  if (taggedTopics === undefined) {
    return <>Loading...</>;
  }

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
      <Box sx={{ my: 2 }}>
        <TopicTable />
      </Box>
    </>
  );
}
PTeamTaggedTopics.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
  references: PropTypes.array.isRequired,
  taggedTopics: PropTypes.object.isRequired,
};
