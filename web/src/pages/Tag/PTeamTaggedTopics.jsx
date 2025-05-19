import { Box, Typography } from "@mui/material";
import PropTypes from "prop-types";

import { sortedSSVCPriorities } from "../../utils/const";

import { SSVCPriorityCountChip } from "./SSVCPriorityCountChip";
import { TopicTable } from "./TopicTables/TopicTable";

export function PTeamTaggedTopics(props) {
  const { pteamId, service, packageId, references, vulnIds, ticketCounts } = props;

  if (vulnIds === undefined || ticketCounts === undefined) {
    return <>Loading...</>;
  }

  return (
    <>
      <Box alignItems="center" display="flex" flexDirection="row" my={2}>
        {sortedSSVCPriorities.map((ssvcPriority) => (
          <SSVCPriorityCountChip
            key={ssvcPriority}
            ssvcPriority={ssvcPriority}
            count={ticketCounts[ssvcPriority]}
            outerSx={{ mr: "10px" }}
          />
        ))}
      </Box>
      <Typography variant="subtitle2" color="textSecondary">
        Default safety impact: {service.service_safety_impact}
      </Typography>
      <Box sx={{ my: 2 }}>
        <TopicTable
          pteamId={pteamId}
          serviceId={service.service_id}
          packageId={packageId}
          vulnIds={vulnIds}
          references={references}
        />
      </Box>
    </>
  );
}
PTeamTaggedTopics.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
  packageId: PropTypes.string.isRequired,
  references: PropTypes.array.isRequired,
  vulnIds: PropTypes.array.isRequired,
  ticketCounts: PropTypes.object.isRequired,
};
