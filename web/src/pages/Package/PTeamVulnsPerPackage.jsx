import { Box, Typography, useMediaQuery, useTheme } from "@mui/material";
import PropTypes from "prop-types";

import { sortedSSVCPriorities } from "../../utils/ssvcUtils";

import { SSVCPriorityCountChip } from "./SSVCPriorityCountChip";
import { VulnCardList } from "./VulnCardList/VulnCardList";
import { VulnTable } from "./VulnTables/VulnTable";

export function PTeamVulnsPerPackage(props) {
  const { pteamId, service, packageId, references, vulnIds, ticketCounts } = props;

  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

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
        {isMdDown ? (
          <VulnCardList
            pteamId={pteamId}
            serviceId={service.service_id}
            packageId={packageId}
            vulnIds={vulnIds}
            references={references}
          />
        ) : (
          <VulnTable
            pteamId={pteamId}
            serviceId={service.service_id}
            packageId={packageId}
            vulnIds={vulnIds}
            references={references}
          />
        )}
      </Box>
    </>
  );
}
PTeamVulnsPerPackage.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
  packageId: PropTypes.string.isRequired,
  references: PropTypes.array.isRequired,
  vulnIds: PropTypes.array.isRequired,
  ticketCounts: PropTypes.object.isRequired,
};
