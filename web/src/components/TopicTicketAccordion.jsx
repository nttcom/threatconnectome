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
  const {
    pteamId,
    topicId,
    serviceId,
    ttStatus,
    dateTimeFormat,
    systemAccount,
    members,
    threat_impact,
  } = props;
  return (
    <Box sx={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
      <Box sx={{ width: "320px", overflowY: "auto" }}>
        <Accordion
          disableGutters
          defaultExpanded
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
                <ThreatImpactStatusChip threatImpact={threat_impact} />
              </Box>
              <Box>/usr/local/lib/python3.7/site-packages/sqlparse-0.4.4.dist-info/METADATA</Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <CardActions sx={{ display: "flex", alignItems: "center", p: 2 }}>
              <Typography mr={1} variant="subtitle2" sx={{ fontWeight: 900, minWidth: "110px" }}>
                Assignees
              </Typography>
              <Box sx={{ maxWidth: 150 }}>
                <AssigneesSelector pteamId={pteamId} topicId={topicId} serviceId={serviceId} />
              </Box>
            </CardActions>
            <Box p={2} display="flex" flexDirection="row" alignItems="flex-start">
              <Typography mr={1} variant="subtitle2" sx={{ fontWeight: 900, minWidth: "110px" }}>
                Status
              </Typography>
              <Box display="flex" flexDirection="column">
                <Box display="flex" alignItems="center">
                  <TopicStatusSelector pteamId={pteamId} topicId={topicId} serviceId={serviceId} />
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
  ttStatus: PropTypes.object.isRequired,
  dateTimeFormat: PropTypes.func.isRequired,
  systemAccount: PropTypes.object.isRequired,
  members: PropTypes.object.isRequired,
  threat_impact: PropTypes.number.isRequired,
};
