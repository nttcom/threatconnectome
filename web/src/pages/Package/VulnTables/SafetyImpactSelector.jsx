import { useSnackbar } from "notistack";
import PropTypes from "prop-types";

import { useUpdateTicketSafetyImpactMutation } from "../../../services/tcApi";
import { errorToString } from "../../../utils/func";

import { SafetyImpactSelectorView } from "./SafetyImpactSelectorView";

export function SafetyImpactSelector(props) {
  const { pteamId, ticket } = props;

  const [updateTicketSafetyImpact] = useUpdateTicketSafetyImpactMutation();

  const { enqueueSnackbar } = useSnackbar();

  const updateTicketFunction = async (requestData) => {
    await updateTicketSafetyImpact({
      pteamId,
      ticketId: ticket.ticket_id,
      data: requestData,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar("Change safety impact succeeded", { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" }),
      );
  };

  const handleRevertedToDefault = async () => {
    const requestData = {
      ticket_safety_impact: null,
      ticket_safety_impact_change_reason: null,
    };
    updateTicketFunction(requestData);
  };

  const handleSave = async (safetyImpact, ticketSafetyImpactChangeReason) => {
    const requestData = {
      ticket_safety_impact: safetyImpact,
      ticket_safety_impact_change_reason: ticketSafetyImpactChangeReason,
    };
    updateTicketFunction(requestData);
  };

  return (
    <SafetyImpactSelectorView
      fixedTicketSafetyImpact={ticket.ticket_safety_impact}
      fixedTicketSafetyImpactChangeReason={ticket.ticket_safety_impact_change_reason}
      onRevertedToDefault={handleRevertedToDefault}
      onSave={handleSave}
    />
  );
}
SafetyImpactSelector.propTypes = {
  pteamId: PropTypes.string.isRequired,
  ticket: PropTypes.object.isRequired,
};
