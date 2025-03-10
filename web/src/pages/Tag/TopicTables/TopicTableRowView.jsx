import { Warning as WarningIcon } from "@mui/icons-material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import {
  Box,
  Button,
  Collapse,
  IconButton,
  TableCell,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import { yellow } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { pickAffectedVersions } from "../../../utils/topicUtils.js";

import { TicketTable } from "./TicketTable.jsx";
import { TicketTableRow } from "./TicketTableRow.jsx";
import { TopicDetailsDrawer } from "./TopicDetailsDrawer.jsx";

export function TopicTableRowView(props) {
  const {
    pteamId,
    serviceId,
    tagId,
    topicId,
    allTags,
    members,
    references,
    topic,
    topicActions,
    tickets,
  } = props;
  const [ticketOpen, setTicketOpen] = useState(false);
  const [topicDrawerOpen, setTopicDrawerOpen] = useState(false);
  const currentTagDict = allTags.find((tag) => tag.tag_id === tagId);

  return (
    <>
      <TableRow>
        <TableCell sx={{ bgcolor: "grey.50" }}>
          <IconButton size="small" onClick={() => setTicketOpen(!ticketOpen)}>
            {ticketOpen ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell sx={{ maxWidth: 300, bgcolor: "grey.50" }}>{topic.title}</TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {tickets.length}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {topic.updated_at}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {pickAffectedVersions(topicActions, currentTagDict.tag_name).map((affectedVersion) => (
            <Box
              key={affectedVersion}
              alignItems="center"
              display="flex"
              flexDirection="row"
              sx={{ ml: 2 }}
            >
              <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
              <Tooltip title={affectedVersion} placement="right">
                <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                  {affectedVersion}
                </Typography>
              </Tooltip>
            </Box>
          ))}
        </TableCell>
        <TableCell align="center" sx={{ bgcolor: "grey.50" }}>
          {"-" /* not yet supported */}
        </TableCell>
        <TableCell align="right" sx={{ bgcolor: "grey.50" }}>
          <Button
            variant="outlined"
            startIcon={<KeyboardDoubleArrowLeftIcon />}
            size="small"
            onClick={() => setTopicDrawerOpen(true)}
          >
            Details
          </Button>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell sx={{ py: 0 }} colSpan={7}>
          <Collapse in={ticketOpen} timeout="auto" unmountOnExit>
            <TicketTable>
              {tickets.map((ticket) => (
                <TicketTableRow
                  key={ticket.ticket_id}
                  pteamId={pteamId}
                  serviceId={serviceId}
                  tagId={tagId}
                  topicId={topicId}
                  allTags={allTags}
                  members={members}
                  references={references}
                  topic={topic}
                  topicActions={topicActions}
                  ticket={ticket}
                />
              ))}
            </TicketTable>
          </Collapse>
        </TableCell>
      </TableRow>
      <TopicDetailsDrawer open={topicDrawerOpen} setOpen={setTopicDrawerOpen} />
    </>
  );
}
TopicTableRowView.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  tagId: PropTypes.string.isRequired,
  topicId: PropTypes.string.isRequired,
  allTags: PropTypes.array.isRequired,
  members: PropTypes.object.isRequired,
  references: PropTypes.array.isRequired,
  topic: PropTypes.object.isRequired,
  topicActions: PropTypes.array.isRequired,
  tickets: PropTypes.array.isRequired,
};
