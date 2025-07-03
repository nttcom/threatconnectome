import { Card, CardContent, Box } from "@mui/material";
import PropTypes from "prop-types";

import { VulnCard } from "./VulnCard";

export function VulnCardList({ pteamId, serviceId, packageId, vulnIds, references }) {
  return (
    <Box>
      {vulnIds.map((vulnId) => (
        <Card key={vulnId} sx={{ mb: 2 }}>
          <CardContent sx={{ p: 2 }}>
            <VulnCard
              pteamId={pteamId}
              serviceId={serviceId}
              packageId={packageId}
              vulnId={vulnId}
              references={references}
            />
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
VulnCardList.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  vulnIds: PropTypes.array.isRequired,
  references: PropTypes.array.isRequired,
};
