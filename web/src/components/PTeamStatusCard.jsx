import { Box, Chip, Stack, TableCell, TableRow, Tooltip, Typography } from "@mui/material";
import { grey, yellow, amber } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React from "react";

import { topicStatusProps, sortedTopicStatus } from "../utils/const";
import { calcTimestampDiff, compareSSVCPriority } from "../utils/func";

import { SSVCPriorityStatusChip } from "./SSVCPriorityStatusChip";

function LineWithTooltip(props) {
  const { topicStatus, ratio, num } = props;
  const constProp = topicStatusProps[topicStatus];

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
  topicStatus: PropTypes.string,
  ratio: PropTypes.number,
  num: PropTypes.number,
};

function DisableLine() {
  const tipAreaHeight = 15;
  const lineHeight = 5;
  const mt = (tipAreaHeight - lineHeight) / 2;

  return (
    <Box sx={{ width: "100%", height: tipAreaHeight + "px" }}>
      <Box
        sx={{
          width: "100%",
          height: lineHeight + "px",
          mt: mt + "px",
          backgroundColor: grey[400],
        }}
      />
    </Box>
  );
}

function StatusRatioGraph(props) {
  const { counts, displaySSVCPriority } = props;
  if (displaySSVCPriority === "empty") return "";
  const keys = ["completed", "scheduled", "acknowledged", "alerted"];
  const total = keys.reduce((ret, key) => ret + counts[key] ?? 0, 0);
  const ratios = keys.reduce((ret, key) => {
    ret[key] = (100 * (counts[key] ?? 0)) / total;
    return ret;
  }, {});

  return (
    <Stack direction="row" spacing={0}>
      {keys.length < 1 && <DisableLine />}
      {keys.map((key) => (
        <LineWithTooltip
          key={key}
          topicStatus={key}
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
  const { onHandleClick, pteam, tag, serviceIds } = props;

  let displaySSVCPriority = "";
  if (!tag.ssvc_priority && tag.status_count["completed"] > 0) {
    displaySSVCPriority = "safe"; // solved all and at least 1 tickets
  } else if (
    !tag.ssvc_priority &&
    sortedTopicStatus.every((topicStatus) => tag.status_count[topicStatus] === 0)
  ) {
    displaySSVCPriority = "empty";
  } else {
    displaySSVCPriority = tag.ssvc_priority ?? "defer";
  }

  // Change the background color and border based on the Alert Threshold value set by the team.
  const highlightCard =
    pteam.alert_ssvc_priority !== "defer" && // disable highlight if threshold is "defer"
    compareSSVCPriority(displaySSVCPriority, pteam.alert_ssvc_priority) <= 0;

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
        <Typography variant="subtitle1" sx={{ overflowWrap: "anywhere" }}>
          {tag.tag_name}
        </Typography>
        {serviceIds &&
          pteam.services
            .filter((service) => serviceIds.includes(service.service_id))
            .sort((a, b) => a.service_name.localeCompare(b.service_name))
            .map((service) => <Chip key={service.service_id} label={service.service_name} />)}
      </TableCell>
      <TableCell align="right" style={{ width: "30%" }}>
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
              Updated ${calcTimestampDiff(tag.updated_at)}
            </Typography>
          </Box>
          <StatusRatioGraph counts={tag.status_count} displaySSVCPriority={tag.ssvc_priority} />
        </Box>
      </TableCell>
    </TableRow>
  );
}

PTeamStatusCard.propTypes = {
  onHandleClick: PropTypes.func.isRequired,
  pteam: PropTypes.object.isRequired,
  tag: PropTypes.shape({
    tag_name: PropTypes.string,
    tag_id: PropTypes.string,
    references: PropTypes.arrayOf(PropTypes.object),
    text: PropTypes.string,
    ssvc_priority: PropTypes.string,
    updated_at: PropTypes.string,
    status_count: PropTypes.object,
  }).isRequired,
  serviceIds: PropTypes.array,
};
