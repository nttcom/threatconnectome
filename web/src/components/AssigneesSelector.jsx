import { Checkbox, ListItemText, MenuItem, Input, Select } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import { getPTeamTopicStatus } from "../slices/pteam";
import { createTopicStatus } from "../utils/api";

export function AssigneesSelector(props) {
  const { pteamId, topicId } = props;

  const { tagId } = useParams();
  const members = useSelector((state) => state.pteam.members); // dispatched by parent
  const topicStatus = useSelector((state) => state.pteam.topicStatus); // dispatched by parent

  const dispatch = useDispatch();
  const [assignees, setAssignees] = useState([]);

  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    if (!topicStatus[topicId]?.[tagId] || !members) return;
    setAssignees(
      (topicStatus[topicId][tagId].assignees ?? []).map(
        (user_id) => members[user_id]?.email ?? "(unknown)",
      ),
    );
  }, [members, tagId, pteamId, topicId, topicStatus]);

  const handleApply = async () => {
    const ttStatus = topicStatus[topicId][tagId];
    const latestUserIds = [...(ttStatus.assignees ?? [])].sort();
    const userIds = Object.values(members)
      .filter((member) => assignees.includes(member.email))
      .map((member) => member.user_id)
      .sort();
    if (JSON.stringify(userIds) === JSON.stringify(latestUserIds)) return; // not modified

    await createTopicStatus(pteamId, topicId, tagId, {
      topic_status: ttStatus.topic_status ?? "acknowledged",
      logging_ids: ttStatus.logging_ids ?? [],
      assignees: userIds,
      note: ttStatus.note,
      scheduled_at: ttStatus.scheduled_at,
    })
      .then(() => {
        dispatch(getPTeamTopicStatus({ pteamId: pteamId, topicId: topicId, tagId: tagId }));
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
    setAssignees(typeof value === "string" ? value.split(",") : value);
  };

  if (!topicStatus[topicId]?.[tagId] || !members) return <></>;

  return (
    <>
      <Select
        multiple
        displayEmpty
        value={assignees}
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
            <Checkbox checked={assignees.includes(member.email)} />
            <ListItemText primary={member.email} />
          </MenuItem>
        ))}
      </Select>
    </>
  );
}

AssigneesSelector.propTypes = {
  pteamId: PropTypes.string.isRequired,
  topicId: PropTypes.string.isRequired,
};
