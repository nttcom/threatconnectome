import { Stack } from "@mui/material";
import PropTypes from "prop-types";

import { VulnCard } from "./VulnCard";

export function VulnCardList({ pteamId, serviceId, packageId, vulnIds, references }) {
  return (
    <Stack spacing={2}>
      {vulnIds.map((vulnId) => (
        <VulnCard
          key={vulnId}
          pteamId={pteamId}
          serviceId={serviceId}
          packageId={packageId}
          vulnId={vulnId}
          references={references}
        />
      ))}
    </Stack>
  );
}
VulnCardList.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  vulnIds: PropTypes.array.isRequired,
  references: PropTypes.array.isRequired,
};
