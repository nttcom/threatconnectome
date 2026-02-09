import {
  Box,
  Chip,
  Stack,
  TableCell,
  TableRow,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { grey, yellow, amber } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";

import { SSVCPriorityStatusChip } from "../../components/SSVCPriorityStatusChip";
import { ticketHandlingStatusProps, sortedTicketHandlingStatus } from "../../utils/const";
import { calcTimestampDiff } from "../../utils/func";
import { compareSSVCPriority } from "../../utils/ssvcUtils";

import { useTranslation } from "react-i18next";

function LineWithTooltip(props) {
  const { ticketHandlingStatus, ratio, num } = props;
  const constProp = ticketHandlingStatusProps[ticketHandlingStatus];

  const tipAreaHeight = 15;
  const lineHeight = 5;
  const mt = (tipAreaHeight - lineHeight) / 2;

  const StyledTooltip = styled((styledProps) => (
    <Tooltip
      arrow
      title={num + " " + constProp.chipLabel}
      classes={{ popper: styledProps.className }}
      {...styledProps}
    />
  ))`
    & .MuiTooltip-tooltip {
      background-color: ${constProp.style.bgcolor};
      color: ${constProp.style.color};
    }
    & .MuiTooltip-arrow {
      color: ${constProp.style.bgcolor};
    }
  `;

  return (
    <StyledTooltip>
      <Box sx={{ width: ratio + "%", height: tipAreaHeight + "px" }}>
        <Box
          sx={{
            width: "100%",
            height: lineHeight + "px",
            mt: mt + "px",
            backgroundColor: constProp.style.bgcolor,
          }}
        />
      </Box>
    </StyledTooltip>
  );
}

LineWithTooltip.propTypes = {
  ticketHandlingStatus: PropTypes.string,
  ratio: PropTypes.number,
  num: PropTypes.number,
};

function StatusRatioGraph(props) {
  const { counts, displaySSVCPriority } = props;

  if (displaySSVCPriority === "empty") return "";
  const keys = ["completed", "scheduled", "acknowledged", "alerted"];
  const total = keys.reduce((ret, key) => ret + (counts[key] ?? 0), 0);
  const ratios = keys.reduce((ret, key) => {
    ret[key] = (100 * (counts[key] ?? 0)) / total;
    return ret;
  }, {});

  return (
    <Stack direction="row" spacing={0}>
      {keys.map((key) => (
        <LineWithTooltip
          key={key}
          ticketHandlingStatus={key}
          ratio={ratios[key] ?? 0}
          num={counts[key] ?? 0}
        />
      ))}
    </Stack>
  );
}

StatusRatioGraph.propTypes = {
  counts: PropTypes.object,
  displaySSVCPriority: PropTypes.string,
};

export function PTeamStatusCard(props) {
  const { onHandleClick, pteam, packageInfo, serviceIds } = props;
  const { t } = useTranslation("status", { keyPrefix: "PTeamStatusCard" });

  let displaySSVCPriority = "";
  if (!packageInfo.ssvc_priority && packageInfo.status_count["completed"] > 0) {
    displaySSVCPriority = "safe"; // solved all and at least 1 tickets
  } else if (
    !packageInfo.ssvc_priority &&
    sortedTicketHandlingStatus.every(
      (ticketHandlingStatus) => packageInfo.status_count[ticketHandlingStatus] === 0,
    )
  ) {
    displaySSVCPriority = "empty";
  } else {
    displaySSVCPriority = packageInfo.ssvc_priority ?? "defer";
  }

  // Change the background color and border based on the Alert Threshold value set by the team.
  const highlightCard =
    pteam.alert_ssvc_priority !== "defer" && // disable highlight if threshold is "defer"
    compareSSVCPriority(displaySSVCPriority, pteam.alert_ssvc_priority) <= 0;

  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

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
        <SSVCPriorityStatusChip displaySSVCPriority={displaySSVCPriority} />
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
          {":"}
          {packageInfo.ecosystem}
        </Typography>
        {serviceIds &&
          pteam.services
            .filter((service) => serviceIds.includes(service.service_id))
            .sort((a, b) => a.service_name.localeCompare(b.service_name))
            .map((service) => <Chip key={service.service_id} label={service.service_name} />)}
      </TableCell>
      <TableCell
        align="right"
        style={{ width: "30%" }}
        sx={{ display: isMdDown ? "none" : undefined }}
      >
        <Box display="flex" flexDirection="column">
          <Box display="flex" flexDirection="row" justifyContent="space-between">
            <Typography
              variant="body2"
              sx={{
                visibility:
                  displaySSVCPriority === "safe" || displaySSVCPriority === "empty"
                    ? "hidden"
                    : "visible",
              }}
            >
              {t("updated", { timeDiff: calcTimestampDiff(packageInfo.updated_at) })}
            </Typography>
          </Box>
          <StatusRatioGraph
            counts={packageInfo.status_count}
            displaySSVCPriority={packageInfo.ssvc_priority}
          />
        </Box>
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
    references: PropTypes.arrayOf(PropTypes.object),
    text: PropTypes.string,
    ssvc_priority: PropTypes.string,
    updated_at: PropTypes.string,
    status_count: PropTypes.object,
    ecosystem: PropTypes.string,
  }).isRequired,
  serviceIds: PropTypes.array,
};
