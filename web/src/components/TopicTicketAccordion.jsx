import { CalendarMonth } from "@mui/icons-material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  CardActions,
  Chip,
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

import { systemAccount } from "../utils/const";
import { dateTimeFormat } from "../utils/func";

import { AssigneesSelector } from "./AssigneesSelector";
import { SSVCPriorityStatusChip } from "./SSVCPriorityStatusChip";
import { TopicStatusSelector } from "./TopicStatusSelector";
import { WarningTooltip } from "./WarningTooltip";

export const TopicTicketAccordion = (props) => {
  const { pteamId, dependency, topicId, ticket, members, defaultExpanded, topicActions } = props;

  const serviceId = dependency.service_id;
  const tagId = dependency.tag_id;
  const target = dependency.target;
  const ticketStatus = ticket.current_ticket_status;
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

  const safetyImpact = {
    description: "The safety impact of the vulnerability. (based on IEC 61508)",
    values: ["Catastrophic", "Critical", "Marginal", "Negligible"],
  };

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
            <SSVCPriorityStatusChip ssvcPriority={ssvcPriority} />
          </Box>
          <Box sx={{ wordBreak: "break-all" }}>{target}</Box>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Box p={2} display="flex" flexDirection="row" alignItems="center">
          <Box sx={{ display: "flex", justifyContent: "start", minWidth: "110px", mr: 1 }}>
            <Typography mr={1} variant="subtitle2" sx={{ fontWeight: 900, mr: 0.5 }}>
              Safety impact
            </Typography>
            <StyledTooltip
              arrow
              title={
                <>
                  <Typography variant="body2">{safetyImpact.description}</Typography>
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
                      value={safetyImpact.values[0]}
                    >
                      {safetyImpact.values.map((value) => (
                        <ToggleButton key={value} value={value} disabled>
                          {value}
                        </ToggleButton>
                      ))}
                    </ToggleButtonGroup>
                  </Box>
                </>
              }
            >
              <HelpOutlineOutlinedIcon color="action" fontSize="small" />
            </StyledTooltip>
          </Box>
          <Chip label={safetyImpact.values[0]} />
        </Box>
        <Box p={2} display="flex" flexDirection="row" alignItems="center">
          <Typography mr={1} variant="subtitle2" sx={{ fontWeight: 900, minWidth: "110px" }}>
            Status
          </Typography>
          <Box display="flex" flexDirection="column">
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
          </Box>
        </Box>
        <CardActions sx={{ display: "flex", alignItems: "center", p: 2 }}>
          <Typography mr={1} variant="subtitle2" sx={{ fontWeight: 900, minWidth: "110px" }}>
            Assignees
          </Typography>
          <Box sx={{ maxWidth: 150 }}>
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
          </Box>
        </CardActions>
        {(ticketStatus.topic_status ?? "alerted") !== "alerted" && (
          <Box
            p={1.5}
            display="flex"
            flexDirection="row"
            justifyContent="flex-end"
            sx={{ color: grey[600] }}
          >
            <Box display="flex" alignItems="flex-end">
              <Typography variant="caption">Last updated by</Typography>
              <Typography ml={0.5} variant="caption" fontWeight={900}>
                {ticketStatus.user_id === systemAccount.uuid
                  ? systemAccount.email
                  : members[ticketStatus.user_id]?.email ?? "not a pteam member"}
              </Typography>
            </Box>
          </Box>
        )}
      </AccordionDetails>
    </Accordion>
  );
};

TopicTicketAccordion.propTypes = {
  pteamId: PropTypes.string.isRequired,
  dependency: PropTypes.object.isRequired,
  topicId: PropTypes.string.isRequired,
  ticket: PropTypes.object.isRequired,
  members: PropTypes.object.isRequired,
  defaultExpanded: PropTypes.bool,
  topicActions: PropTypes.array,
};
TopicTicketAccordion.defaultProps = {
  defaultExpanded: false,
  topicActions: [],
};
