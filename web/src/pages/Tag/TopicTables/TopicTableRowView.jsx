import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardDoubleArrowLeftIcon from "@mui/icons-material/KeyboardDoubleArrowLeft";
import { Button, Collapse, IconButton, TableCell, TableRow } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { ssvcPriorityProps } from "../../../utils/const.js";
import { searchWorstSSVC } from "../../../utils/func.js";
import { pickAffectedVersions } from "../../../utils/topicUtils.js";
import { VulnerabilityDrawer } from "../../Vulnerability/VulnerabilityDrawer";

import { TicketTable } from "./TicketTable.jsx";
import { TicketTableRow } from "./TicketTableRow.jsx";

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
  const [ticketOpen, setTicketOpen] = useState(true);
  const [topicDrawerOpen, setTopicDrawerOpen] = useState(false);
  const currentTagDict = allTags.find((tag) => tag.tag_id === tagId);

  const affectedVersions = pickAffectedVersions(topicActions, currentTagDict.tag_name);

  return (
    <>
      <TableRow>
        <TableCell
          sx={{
            bgcolor: "grey.50",
            borderLeft: `solid 5px ${ssvcPriorityProps[searchWorstSSVC(tickets)].style.bgcolor}`,
          }}
        >
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
          {affectedVersions.map((affectedVersion, index) =>
            index + 1 === affectedVersions.length ? (
              affectedVersion
            ) : (
              <>
                {affectedVersion}
                <br />
              </>
            ),
          )}
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
                  members={members}
                  references={references}
                  topicActions={topicActions}
                  ticket={ticket}
                />
              ))}
            </TicketTable>
          </Collapse>
        </TableCell>
      </TableRow>
      <VulnerabilityDrawer
        open={topicDrawerOpen}
        setOpen={setTopicDrawerOpen}
        pteamId={pteamId}
        serviceId={serviceId}
        serviceTagId={tagId}
        topicId={topicId}
      />
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
