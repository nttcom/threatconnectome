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

import { AssigneesSelector } from "./AssigneesSelector";
import { ThreatImpactStatusChip } from "./ThreatImpactStatusChip";
import { TopicStatusSelector } from "./TopicStatusSelector";
import { WarningTooltip } from "./WarningTooltip";

export const TopicTicketAccordion = (props) => {
  const { pteamId, topicId, serviceId, ttStatus, dateTimeFormat, systemAccount, members } = props;
  console.log(typeof systemAccount);
  return (
    <Box display="flex" flexDirection="column" sx={{ height: "350px" }}>
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="baseline"
        sx={{ width: "320px", overflowY: "scroll" }}
      >
        {[...Array(3)].map((_, i) => (
          <Accordion key={i} disableGutters defaultExpanded={i === 0 ? true : false}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ backgroundColor: grey[50] }}>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Box sx={{ mr: 1 }}>
                  <ThreatImpactStatusChip threatImpact={1} />
                </Box>
                <Box>/usr/local/lib/python3.7/site-packages/sqlparse-0.4.4.dist-info/METADATA</Box>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {/* <Box display="flex" alignItems="baseline" p={2}>
                <Typography mr={2} variant="subtitle2" sx={{ fontWeight: 900 }}>
                  Threat impact
                </Typography>
                <ThreatImpactChip threatImpact={topic.threat_impact ?? 4} />
              </Box> */}
              <CardActions sx={{ display: "flex", alignItems: "center", p: 2 }}>
                <Typography mr={1} variant="subtitle2" sx={{ fontWeight: 900, minWidth: "110px" }}>
                  Assignees
                </Typography>
                <Box sx={{ maxWidth: 200 }}>
                  <AssigneesSelector pteamId={pteamId} topicId={topicId} serviceId={serviceId} />
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
                      topicId={topicId}
                      serviceId={serviceId}
                    />
                    {(ttStatus.topic_status ?? "alerted") === "alerted" && (
                      <WarningTooltip message="No one has acknowledged this topic" />
                    )}
                  </Box>
                  {(ttStatus.topic_status ?? "scheduled") === "scheduled" &&
                    ttStatus.scheduled_at && (
                      <Box display="flex" alignItems="flex-end">
                        <Typography ml={0.5} variant="caption">
                          <CalendarMonth fontSize="small" sx={{ color: grey[700], mb: -0.7 }} />
                          {dateTimeFormat(ttStatus.scheduled_at)}
                        </Typography>
                      </Box>
                    )}
                </Box>
              </Box>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
      {(ttStatus.topic_status ?? "alerted") !== "alerted" && (
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
              {ttStatus.user_id === systemAccount.uuid
                ? systemAccount.email
                : members[ttStatus.user_id]?.email ?? "not a pteam member"}
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
};

TopicTicketAccordion.propTypes = {
  pteamId: PropTypes.string.isRequired,
  topicId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  ttStatus: PropTypes.any.isRequired,
  dateTimeFormat: PropTypes.any.isRequired,
  systemAccount: PropTypes.any.isRequired,
  members: PropTypes.any.isRequired,
};
