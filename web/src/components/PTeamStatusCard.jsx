import { Box, Chip, Stack, TableCell, TableRow, Tooltip, Typography } from "@mui/material";
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

function ServiceChips(props) {
  const { references } = props;
  const unduplicatedServices = [...new Set(references.map((ref) => ref.service))].filter(
    (service) => service !== "",
  );

  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const selectedService = params.get("service") ?? "";

  const handleSelectService = (service) => {
    if (service === selectedService) {
      params.delete("service");
    } else {
      params.set("service", service);
      params.set("page", 1); // reset page
    }
    navigate(location.pathname + "?" + params.toString());
  };

  return (
    <Box sx={{ overflowX: "auto", whiteSpace: "nowrap" }}>
      {unduplicatedServices.map((service) => (
        <Chip
          key={service}
          label={service}
          variant={service === selectedService ? "" : "outlined"}
          size="small"
          onClick={(event) => {
            handleSelectService(service);
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
ServiceChips.propTypes = {
  references: PropTypes.arrayOf(
    PropTypes.shape({
      target: PropTypes.string,
      version: PropTypes.string,
      service: PropTypes.string,
    }),
  ).isRequired,
};

export function PTeamStatusCard(props) {
  const { onHandleClick, tag } = props;

  return (
    <TableRow
      onClick={onHandleClick}
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
        <ServiceChips references={tag.references}></ServiceChips>
      </TableCell>
      <TableCell align="right" style={{ width: "30%" }}>
        <Box display="flex" flexDirection="column">
          <Box display="flex" flexDirection="row" justifyContent="space-between">
            <Typography variant="body2">
              {`Updated ${calcTimestampDiff(tag.updated_at)}`}
            </Typography>
          </Box>
          <StatusRatioGraph counts={tag.status_count ?? []} threatImpact={tag.threat_impact ?? 4} />
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
    threat_impact: PropTypes.number,
    updated_at: PropTypes.string,
    status_count: PropTypes.object,
  }).isRequired,
};
