import { Checkbox, ListItemText, MenuItem, Input, Select, FormControl } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";

import { useUpdateTicketMutation } from "../../../services/tcApi";
import { errorToString, setEquals } from "../../../utils/func";

export function AssigneesSelectorVulnTable(props) {
  const { pteamId, serviceId, vulnId, packageId, ticketId, currentAssigneeIds, members } = props;

  const [assigneeUserIds, setAssigneeUserIds] = useState(
    members
      .filter((member) => currentAssigneeIds.includes(member.user_id))
      .map((member) => member.user_id),
  );

  const { enqueueSnackbar } = useSnackbar();

  const [updateTicket] = useUpdateTicketMutation();

  const handleApply = async () => {
    const newAssigneeIds = members
      .filter((member) => assigneeUserIds.includes(member.user_id))
      .map((member) => member.user_id);
    if (setEquals(new Set(newAssigneeIds), new Set(currentAssigneeIds))) return; // not modified

    await updateTicket({
      path: { pteam_id: pteamId, ticket_id: ticketId },
      body: { ticket_status: { assignees: newAssigneeIds } },
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar("Change assignees succeeded", { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" }),
      );
  };

  const handleAssigneesChange = (event) => {
    const {
      target: { value },
    } = event;
    setAssigneeUserIds((typeof value === "string" ? value.split(",") : value).sort());
  };

  if (!pteamId || !serviceId || !vulnId || !packageId || !ticketId || !members) return <></>;

  return (
    <FormControl sx={{ width: 160 }} size="small">
      <Select
        multiple
        displayEmpty
        value={assigneeUserIds}
        onChange={handleAssigneesChange}
        onClose={handleApply}
        input={<Input sx={{ display: "flex", fontSize: 14 }} />}
        renderValue={(selected) => {
          return selected.length === 0 ? (
            <em>Select assignees</em>
          ) : (
            members
              .filter((member) => selected.includes(member.user_id))
              .map((member) => member.email)
              .join(", ")
          );
        }}
        MenuProps={{
          PaperProps: {
            style: {},
          },
        }}
        inputProps={{
          "area-label": "Without label",
        }}
        notched="true" /* to avoid Warning: Received `true` for a non-boolean attribute `notched` */
      >
        <MenuItem disabled value="" sx={{ fontSize: 14 }}>
          <em>Select assignees</em>
        </MenuItem>
        {members.map((member) => (
          <MenuItem key={member.user_id} value={member.user_id}>
            <Checkbox checked={assigneeUserIds.includes(member.user_id)} />
            <ListItemText primary={member.email} sx={{ "& span": { fontSize: 14 } }} />
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

AssigneesSelectorVulnTable.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  ticketId: PropTypes.string.isRequired,
  currentAssigneeIds: PropTypes.array.isRequired,
  members: PropTypes.array.isRequired,
};
