import {
  Chip,
  TableCell,
  TableRow,
  Typography,
} from "@mui/material";
import { grey, yellow, amber } from "@mui/material/colors";
import PropTypes from "prop-types";

import { SSVCPriorityStatusChip } from "../../components/SSVCPriorityStatusChip";
import { compareSSVCPriority } from "../../utils/ssvcUtils";

export function PTeamStatusCard(props) {
  const { onHandleClick, pteam, packageInfo, serviceIds } = props;

  // Change the background color and border based on the Alert Threshold value set by the team.
  const highlightCard =
    pteam.alert_ssvc_priority !== "defer" && // disable highlight if threshold is "defer"
    compareSSVCPriority(packageInfo.ssvc_priority, pteam.alert_ssvc_priority) <= 0;

  return (
    <TableRow
      onClick={onHandleClick}
      sx={{
        border: "2px",
        borderBottom: "2px",
        ...(highlightCard && {
          boxShadow: `inset 0 0 0 2px ${amber[100]}`,
          backgroundColor: yellow[50],
        }),
        cursor: "pointer",
        "&:last-child td, &:last-child th": { border: 0 },
        "&:hover": { bgcolor: grey[100] },
      }}
    >
      <TableCell component="th" scope="row" style={{ width: "5%" }}>
        <SSVCPriorityStatusChip displaySSVCPriority={packageInfo.ssvc_priority} />
      </TableCell>
      <TableCell component="th" scope="row" style={{ maxWidth: 0 }}>
        <Typography
          variant="subtitle1"
          sx={{
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            display: "block",
            maxWidth: "100%",
          }}
        >
          {packageInfo.package_name}
        </Typography>
        {serviceIds &&
          pteam.services
            .filter((service) => serviceIds.includes(service.service_id))
            .sort((a, b) => a.service_name.localeCompare(b.service_name))
            .map((service) => <Chip key={service.service_id} label={service.service_name} />)}
      </TableCell>
      <TableCell style={{ width: "15%" }}>
        <Typography variant="body2">{packageInfo.ecosystem}</Typography>
      </TableCell>
      <TableCell style={{ width: "15%" }}>
        <Typography variant="body2" color="text.secondary">
          {"-"}
        </Typography>
      </TableCell>
    </TableRow>
  );
}

PTeamStatusCard.propTypes = {
  onHandleClick: PropTypes.func.isRequired,
  pteam: PropTypes.object.isRequired,
  packageInfo: PropTypes.shape({
    package_name: PropTypes.string,
    package_id: PropTypes.string,
    ssvc_priority: PropTypes.string,
    ecosystem: PropTypes.string,
  }).isRequired,
  serviceIds: PropTypes.array,
};
