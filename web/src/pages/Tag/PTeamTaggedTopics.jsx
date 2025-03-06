import { Box, Typography } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

import { TopicTable } from "./TopicTables/TopicTable";
import { sortedSSVCPriorities } from "../../utils/const";

import { SSVCPriorityCountChip } from "./SSVCPriorityCountChip";

export function PTeamTaggedTopics(props) {
  const { pteamId, service, references, taggedTopics } = props;

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
      <Typography variant="subtitle2" color="textSecondary">
        Default safety impact: {service.service_safety_impact}
      </Typography>
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
