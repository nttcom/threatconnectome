import {
  ChatBubbleOutline as ChatBubbleOutlineIcon,
  ChatOutlined as ChatOutlinedIcon,
} from "@mui/icons-material";
import { Box, Chip, Stack, TableCell, TableRow, Tooltip, Typography } from "@mui/material";
import { tooltipClasses } from "@mui/material/Tooltip";
import { grey } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React from "react";
import { useLocation, useNavigate } from "react-router";

import { topicStatusProps } from "../utils/const";
import { calcTimestampDiff } from "../utils/func";

import { ThreatImpactStatusChip } from "./ThreatImpactStatusChip";

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
  const { counts, threatImpact } = props;
  if ((counts ?? []).length === 0) return "";
  let keys = [];
  if (threatImpact < 4) {
    keys = ["scheduled", "acknowledged", "alerted"];
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
  threatImpact: PropTypes.number,
};

function GroupChips(props) {
  const { references } = props;
  const unduplicatedGroups = [...new Set(references.map((ref) => ref.group))].filter(
    (group) => group !== ""
  );

  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const selectedGroup = params.get("group") ?? "";

  const handleSelectGroup = (group) => {
    if (group === selectedGroup) {
      params.delete("group");
    } else {
      params.set("group", group);
      params.set("page", 1); // reset page
    }
    navigate(location.pathname + "?" + params.toString());
  };

  return (
    <Box sx={{ overflowX: "auto", whiteSpace: "nowrap" }}>
      {unduplicatedGroups.map((group) => (
        <Chip
          key={group}
          label={group}
          variant={group === selectedGroup ? "" : "outlined"}
          size="small"
          onClick={(event) => {
            handleSelectGroup(group);
            event.stopPropagation(); // avoid propagation of click event to parent
          }}
          sx={{
            textTransform: "none",
            marginRight: "5px",
          }}
        />
      ))}
    </Box>
  );
}
GroupChips.propTypes = {
  references: PropTypes.arrayOf(
    PropTypes.shape({
      target: PropTypes.string,
      version: PropTypes.string,
      group: PropTypes.string,
    })
  ).isRequired,
};

export function PTeamStatusCard(props) {
  const { handleClick, tag } = props;

  const CommentTooltip = styled(({ className, ...props }) => (
    <Tooltip {...props} classes={{ popper: className }} />
  ))(({ theme }) => ({
    [`& .${tooltipClasses.tooltip}`]: {
      backgroundColor: grey[50],
      color: "rgba(0, 0, 0, 0.87)",
      maxWidth: 480,
      fontSize: theme.typography.pxToRem(12),
      border: "1px solid #dadde9",
    },
  }));

  return (
    <TableRow
      onClick={handleClick}
      sx={{
        cursor: "pointer",
        "&:last-child td, &:last-child th": { border: 0 },
        "&:hover": { bgcolor: grey[100] },
      }}
    >
      <TableCell component="th" scope="row" style={{ width: "5%" }}>
        <ThreatImpactStatusChip
          threatImpact={tag.threat_impact ?? 4}
          statusCounts={tag.status_count ?? []}
        />
      </TableCell>
      <TableCell component="th" scope="row" style={{ maxWidth: 0 }}>
        <Typography variant="subtitle1" sx={{ overflowWrap: "anywhere" }}>
          {tag.tag_name}
        </Typography>
        <GroupChips references={tag.references}></GroupChips>
      </TableCell>
      <TableCell align="right" style={{ width: "30%" }}>
        <Box display="flex" flexDirection="column">
          <Box display="flex" flexDirection="row" justifyContent="space-between">
            <Typography variant="body2">
              {`Updated ${calcTimestampDiff(tag.updated_at)}`}
            </Typography>
            {tag.text ? (
              <CommentTooltip title={<Typography variant="body2">{tag.text}</Typography>}>
                <ChatOutlinedIcon />
              </CommentTooltip>
            ) : (
              <ChatBubbleOutlineIcon sx={{ color: grey[300] }} />
            )}
          </Box>
          <StatusRatioGraph counts={tag.status_count ?? []} threatImpact={tag.threat_impact ?? 4} />
        </Box>
      </TableCell>
    </TableRow>
  );
}

PTeamStatusCard.propTypes = {
  handleClick: PropTypes.func.isRequired,
  tag: PropTypes.shape({
    tag_name: PropTypes.string,
    tag_id: PropTypes.string,
    references: PropTypes.arrayOf(PropTypes.object),
    text: PropTypes.string,
    threat_impact: PropTypes.number,
    updated_at: PropTypes.string,
    status_count: PropTypes.object,
  }).isRequired,
};
