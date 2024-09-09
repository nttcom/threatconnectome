import { Box, Chip, Stack, TableCell, TableRow, Tooltip, Typography } from "@mui/material";
import { grey, yellow, amber } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";

import { ssvcPriorityProps, topicStatusProps } from "../utils/const";
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
  const { counts, ssvcPriority } = props;
  if ((counts ?? []).length === 0) return "";
  let keys = [];
  if (
    compareSSVCPriority(ssvcPriority, "defer") < 0 ||
    (compareSSVCPriority(ssvcPriority, "defer") === 0 && counts.completed > 0)
  ) {
    keys = ["completed", "scheduled", "acknowledged", "alerted"];
  }
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
  ssvcPriority: PropTypes.string,
};

export function PTeamStatusCard(props) {
  const { onHandleClick, tag, serviceIds } = props;
  const [alertThreshold, setAlertThreshold] = useState(null);

  const pteam = useSelector((state) => state.pteam.pteam);

  const priorityProp = ssvcPriorityProps[tag.ssvc_priority || "defer"];
  const ssvcPriority =
    priorityProp.displayName === "Defer" && tag.status_count["completed"] > 0
      ? "safe" // solved all and at least 1 tickets
      : priorityProp.displayName;

  useEffect(() => {
    if (pteam) {
      setAlertThreshold(pteam.alert_ssvc_priority);
    }
  }, [pteam]);

  return (
    <TableRow
      onClick={onHandleClick}
      sx={{
        border: "2px",
        borderBottom: "2px",
        // Change the background color and border based on the Alert Threshold value set by the team.
        ...(alertThreshold !== null &&
          compareSSVCPriority(ssvcPriority, "defer") !== 0 &&
          compareSSVCPriority(ssvcPriority, alertThreshold) <= 0 && {
            boxShadow: `inset 0 0 0 2px ${amber[100]}`,
            backgroundColor: yellow[50],
          }),
        cursor: "pointer",
        "&:last-child td, &:last-child th": { border: 0 },
        "&:hover": { bgcolor: grey[100] },
      }}
    >
      <TableCell component="th" scope="row" style={{ width: "5%" }}>
        <SSVCPriorityStatusChip ssvcPriority={ssvcPriority} />
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
            <Typography variant="body2">
              {`Updated ${calcTimestampDiff(tag.updated_at)}`}
            </Typography>
          </Box>
          <StatusRatioGraph
            counts={tag.status_count ?? []}
            ssvcPriority={tag.ssvc_priority || "defer"}
          />
        </Box>
      </TableCell>
    </TableRow>
  );
}

PTeamStatusCard.propTypes = {
  onHandleClick: PropTypes.func.isRequired,
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
