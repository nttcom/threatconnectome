import { Checkbox, ListItemText, MenuItem, Input, Select } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch } from "react-redux";

import { getTicketsRelatedToServiceTopicTag } from "../slices/pteam";
import { setTicketStatus } from "../utils/api";
import { setEquals } from "../utils/func";

export function AssigneesSelector(props) {
  const { pteamId, serviceId, topicId, tagId, ticketId, currentAssigneeIds, members } = props;

  const [assigneeEmails, setAssigneeEmails] = useState(
    Object.values(members)
      .filter((member) => currentAssigneeIds.includes(member.user_id))
      .map((member) => member.email),
  );

  const dispatch = useDispatch();

  const { enqueueSnackbar } = useSnackbar();

  const handleApply = async () => {
    const newAssigneeIds = Object.values(members)
      .filter((member) => assigneeEmails.includes(member.email))
      .map((member) => member.user_id);
    if (setEquals(new Set(newAssigneeIds), new Set(currentAssigneeIds))) return; // not modified

    await setTicketStatus(pteamId, serviceId, ticketId, { assignees: newAssigneeIds })
      .then(() => {
        dispatch(
          getTicketsRelatedToServiceTopicTag({
            pteamId: pteamId,
            serviceId: serviceId,
            topicId: topicId,
            tagId: tagId,
          }),
        );
        enqueueSnackbar("Change assignees succeeded", { variant: "success" });
      })
      .catch((error) => {
        const resp = error.response;
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" },
        );
      });
  };

  const handleAssigneesChange = (event) => {
    const {
      target: { value },
    } = event;
    setAssigneeEmails((typeof value === "string" ? value.split(",") : value).sort());
  };

  if (!pteamId || !serviceId || !topicId || !tagId || !ticketId || !members) return <></>;

  return (
    <>
      <Select
        multiple
        displayEmpty
        value={assigneeEmails}
        onChange={handleAssigneesChange}
        onClose={handleApply}
        input={<Input sx={{ display: "flex" }} />}
        renderValue={(selected) => {
          return selected.length === 0 ? <em>select</em> : selected.join(", ");
        }}
        MenuProps={{
          PaperProps: {
            style: {},
          },
        }}
        inputProps={{
          "area-label": "Without label",
        }}
      >
        <MenuItem disabled value="">
          <em>select assignees</em>
        </MenuItem>
        {Object.values(members).map((member) => (
          <MenuItem key={member.user_id} value={member.email}>
            <Checkbox checked={assigneeEmails.includes(member.email)} />
            <ListItemText primary={member.email} />
          </MenuItem>
        ))}
      </Select>
    </>
  );
}

AssigneesSelector.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  topicId: PropTypes.string.isRequired,
  tagId: PropTypes.string.isRequired,
  ticketId: PropTypes.string.isRequired,
  currentAssigneeIds: PropTypes.array.isRequired,
  members: PropTypes.object.isRequired,
};
