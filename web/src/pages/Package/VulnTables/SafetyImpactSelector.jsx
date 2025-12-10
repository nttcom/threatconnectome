import { useSnackbar } from "notistack";
import PropTypes from "prop-types";

import { useUpdateTicketMutation } from "../../../services/tcApi";
import { errorToString } from "../../../utils/func";

import { SafetyImpactSelectorView } from "./SafetyImpactSelectorView";

export function SafetyImpactSelector(props) {
  const { pteamId, ticket } = props;

  const [updateTicket] = useUpdateTicketMutation();

  const { enqueueSnackbar } = useSnackbar();

  const updateTicketFunction = async (requestData) => {
    await updateTicket({
      path: { pteam_id: pteamId, ticket_id: ticket.ticket_id },
      body: requestData,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar("Change safety impact succeeded", { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" }),
      );
  };

  const handleSave = async (safetyImpact, ticketSafetyImpactChangeReason) => {
    const requestData = {
      ticket_safety_impact: safetyImpact,
      ticket_safety_impact_change_reason:
        ticketSafetyImpactChangeReason === "" ? null : ticketSafetyImpactChangeReason,
    };
    updateTicketFunction(requestData);
  };

  return (
    <SafetyImpactSelectorView
      fixedTicketSafetyImpact={ticket.ticket_safety_impact}
      fixedTicketSafetyImpactChangeReason={ticket.ticket_safety_impact_change_reason}
      onSave={handleSave}
    />
  );
}
SafetyImpactSelector.propTypes = {
  pteamId: PropTypes.string.isRequired,
  ticket: PropTypes.object.isRequired,
};
