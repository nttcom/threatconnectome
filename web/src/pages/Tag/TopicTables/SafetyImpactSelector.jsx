import { useSnackbar } from "notistack";
import PropTypes from "prop-types";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useUpdateTicketSafetyImpactMutation } from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";

import { SafetyImpactSelectorView } from "./SafetyImpactSelectorView";

export function SafetyImpactSelector(props) {
  const { pteamId, ticket } = props;

  const skip = useSkipUntilAuthUserIsReady();

  const [updateTicketSafetyImpact] = useUpdateTicketSafetyImpactMutation();

  const { enqueueSnackbar } = useSnackbar();

  if (skip) return <></>;

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
      reason_safety_impact: null,
    };
    updateTicketFunction(requestData);
  };

  const handleSave = async (safetyImpact, reasonSafetyImpact) => {
    const requestData = {
      ticket_safety_impact: safetyImpact,
      reason_safety_impact: reasonSafetyImpact,
    };
    updateTicketFunction(requestData);
  };

  return (
    <SafetyImpactSelectorView
      fixedTicketSafetyImpact={ticket.ticket_safety_impact}
      fixedReasonSafetyImpact={ticket.reason_safety_impact}
      onRevertedToDefault={handleRevertedToDefault}
      onSave={handleSave}
    />
  );
}
SafetyImpactSelector.propTypes = {
  pteamId: PropTypes.string.isRequired,
  ticket: PropTypes.object.isRequired,
};
