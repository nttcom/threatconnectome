import { CalendarMonth } from "@mui/icons-material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  CardActions,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";

import { systemAccount } from "../utils/const";
import { dateTimeFormat } from "../utils/func";

import { AssigneesSelector } from "./AssigneesSelector";
import { ThreatImpactStatusChip } from "./ThreatImpactStatusChip";
import { TopicStatusSelector } from "./TopicStatusSelector";
import { WarningTooltip } from "./WarningTooltip";

const ssvcPriorityToThreatImpact = (ssvcPriority) =>
  ({
    immediate: 1,
    out_of_cycle: 2,
    scheduled: 3,
    defer: 4,
  })[ssvcPriority];

export const TopicTicketAccordion = (props) => {
  const { pteamId, dependency, topicId, ticket, members, defaultExpanded } = props;

  const serviceId = dependency.service_id;
  const tagId = dependency.tag_id;
  const target = dependency.target;
  const ticketStatus = ticket.current_ticket_status;
  const threatImpact = ssvcPriorityToThreatImpact(ticket.ssvc_deployer_priority);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
      <Box sx={{ width: "320px", overflowY: "auto" }}>
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
                <ThreatImpactStatusChip threatImpact={threatImpact} />
              </Box>
              <Box>{target}</Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <CardActions sx={{ display: "flex", alignItems: "center", p: 2 }}>
              <Typography mr={1} variant="subtitle2" sx={{ fontWeight: 900, minWidth: "110px" }}>
                Assignees
              </Typography>
              <Box sx={{ maxWidth: 150 }}>
                <AssigneesSelector
                  pteamId={pteamId}
                  serviceId={serviceId}
                  topicId={topicId}
                  tagId={tagId}
                  ticketId={ticket.ticket_id}
                  currentAssigneeIds={ticket.current_ticket_status.assignees}
                  members={members}
                />
              </Box>
            </CardActions>
            <Box p={2} display="flex" flexDirection="row" alignItems="flex-start">
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
      </Box>
    </Box>
  );
};

TopicTicketAccordion.propTypes = {
  pteamId: PropTypes.string.isRequired,
  dependency: PropTypes.object.isRequired,
  topicId: PropTypes.string.isRequired,
  ticket: PropTypes.object.isRequired,
  members: PropTypes.object.isRequired,
  defaultExpanded: PropTypes.bool,
};
TopicTicketAccordion.defaultProps = {
  defaultExpanded: false,
};
