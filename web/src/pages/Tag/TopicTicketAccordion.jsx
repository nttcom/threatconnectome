import { CalendarMonth } from "@mui/icons-material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Chip,
  Grid,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import { tooltipClasses } from "@mui/material/Tooltip";
import { grey } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React from "react";

import { SSVCPriorityStatusChip } from "../../components/SSVCPriorityStatusChip";
import {
  safetyImpactDescription,
  safetyImpactProps,
  sortedSafetyImpacts,
  systemAccount,
} from "../../utils/const";
import { dateTimeFormat } from "../../utils/func";

import { AssigneesSelector } from "./AssigneesSelector";
import { TopicStatusSelector } from "./TopicStatusSelector";
import { WarningTooltip } from "./WarningTooltip";

export function TopicTicketAccordion(props) {
  const {
    pteamId,
    dependency,
    topicId,
    ticket,
    serviceSafetyImpact,
    members,
    defaultExpanded = false,
    topicActions = [],
  } = props;

  const serviceId = dependency.service_id;
  const tagId = dependency.tag_id;
  const target = dependency.target;
  const ticketStatus = ticket.ticket_status;
  const ssvcPriority = ticket.ssvc_deployer_priority || "defer";

  const StyledTooltip = styled(({ className, ...props }) => (
    <Tooltip {...props} classes={{ popper: className }} />
  ))(() => ({
    [`& .${tooltipClasses.arrow}`]: {
      "&:before": {
        border: "1px solid #dadde9",
      },
      color: "#f5f5f9",
    },
    [`& .${tooltipClasses.tooltip}`]: {
      backgroundColor: "#f5f5f9",
      color: "rgba(0, 0, 0, 0.87)",
      border: "1px solid #dadde9",
    },
  }));

  const serviceSafetyImpactDisplayName = safetyImpactProps[serviceSafetyImpact].displayName;

  return (
    <Accordion
      disableGutters
      defaultExpanded={defaultExpanded}
      sx={{
        borderTop: 1,
        borderBottom: 1,
        borderColor: "divider",
        "&:not(:last-child)": { borderBottom: 0 },
        "&::before": { display: "none" },
      }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ backgroundColor: grey[50] }}>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Box sx={{ mr: 1 }}>
            <SSVCPriorityStatusChip displaySSVCPriority={ssvcPriority} />
          </Box>
          <Box sx={{ wordBreak: "break-all" }}>{target}</Box>
        </Box>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 3 }}>
        <Grid container sx={{ alignItems: "center", pb: 2 }}>
          <Grid item xs={5} sx={{ display: "flex" }}>
            <Typography mr={1} variant="subtitle2" sx={{ fontWeight: "bold", mr: 0.5 }}>
              Safety impact
            </Typography>
            <StyledTooltip
              arrow
              title={
                <>
                  <Typography variant="body2">{safetyImpactDescription}</Typography>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      p: 1,
                    }}
                  >
                    <ToggleButtonGroup
                      color="primary"
                      size="small"
                      orientation="vertical"
                      value={serviceSafetyImpactDisplayName}
                    >
                      {sortedSafetyImpacts.map((safetyImpact) => {
                        const displayName = safetyImpactProps[safetyImpact].displayName;
                        return (
                          <ToggleButton key={safetyImpact} value={displayName} disabled>
                            {displayName}
                          </ToggleButton>
                        );
                      })}
                    </ToggleButtonGroup>
                  </Box>
                </>
              }
            >
              <HelpOutlineOutlinedIcon color="action" fontSize="small" />
            </StyledTooltip>
          </Grid>
          <Grid item xs={7}>
            <Chip label={serviceSafetyImpactDisplayName} />
          </Grid>
        </Grid>
        <Grid container sx={{ alignItems: "center", pb: 2 }}>
          <Grid item xs={5}>
            <Typography mr={1} variant="subtitle2" sx={{ fontWeight: "bold", minWidth: "110px" }}>
              Status
            </Typography>
          </Grid>
          <Grid item xs={7}>
            <Box display="flex" alignItems="center">
              <TopicStatusSelector
                pteamId={pteamId}
                serviceId={serviceId}
                topicId={topicId}
                tagId={tagId}
                ticketId={ticket.ticket_id}
                currentStatus={ticketStatus}
                topicActions={topicActions}
              />
              {(ticketStatus.topic_status ?? "alerted") === "alerted" && (
                <WarningTooltip message="No one has acknowledged this topic" />
              )}
            </Box>
            {(ticketStatus.topic_status ?? "scheduled") === "scheduled" &&
              ticketStatus.scheduled_at && (
                <Box display="flex" alignItems="flex-end">
                  <Typography ml={0.5} variant="caption">
                    <CalendarMonth fontSize="small" sx={{ color: grey[700], mb: -0.7 }} />
                    {dateTimeFormat(ticketStatus.scheduled_at)}
                  </Typography>
                </Box>
              )}
          </Grid>
        </Grid>
        <Grid container sx={{ alignItems: "center", pb: 2 }}>
          <Grid item xs={5}>
            <Typography mr={1} variant="subtitle2" sx={{ fontWeight: "bold", minWidth: "110px" }}>
              Assignees
            </Typography>
          </Grid>
          <Grid item xs={7}>
            <AssigneesSelector
              key={ticketStatus.assignees.join("")}
              pteamId={pteamId}
              serviceId={serviceId}
              topicId={topicId}
              tagId={tagId}
              ticketId={ticket.ticket_id}
              currentAssigneeIds={ticketStatus.assignees}
              members={members}
            />
          </Grid>
        </Grid>
        {(ticketStatus.topic_status ?? "alerted") !== "alerted" && (
          <Box sx={{ textAlign: "right", color: grey[600] }}>
            <Typography variant="caption">Last updated by</Typography>
            <Typography ml={0.5} variant="caption" fontWeight={900}>
              {ticketStatus.user_id === systemAccount.uuid
                ? systemAccount.email
                : (members[ticketStatus.user_id]?.email ?? "not a pteam member")}
            </Typography>
          </Box>
        )}
      </AccordionDetails>
    </Accordion>
  );
}

TopicTicketAccordion.propTypes = {
  pteamId: PropTypes.string.isRequired,
  dependency: PropTypes.object.isRequired,
  topicId: PropTypes.string.isRequired,
  ticket: PropTypes.object.isRequired,
  serviceSafetyImpact: PropTypes.string.isRequired,
  members: PropTypes.object.isRequired,
  defaultExpanded: PropTypes.bool,
  topicActions: PropTypes.array,
};
