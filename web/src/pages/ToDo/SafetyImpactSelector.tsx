import { useSnackbar } from "notistack";
import { useTranslation } from "react-i18next";

import type { SafetyImpactEnum, TicketUpdateRequest } from "../../../types/types.gen";
import { useUpdateTicketMutation } from "../../services/tcApi";
import { errorToString } from "../../utils/func";

import { SafetyImpactSelectorView } from "./SafetyImpactSelectorView";

type SafetyImpactSelectorTicket = {
  ticket_id: string;
  ticket_safety_impact: SafetyImpactEnum | null;
  ticket_safety_impact_change_reason: string | null;
};

type SafetyImpactSelectorProps = {
  pteamId: string;
  ticket: SafetyImpactSelectorTicket;
};

export function SafetyImpactSelector(props: SafetyImpactSelectorProps) {
  const { pteamId, ticket } = props;
  const { t } = useTranslation("toDo", { keyPrefix: "SafetyImpactSelector" });

  const [updateTicket] = useUpdateTicketMutation();

  const { enqueueSnackbar } = useSnackbar();

  const updateTicketFunction = async (requestData: TicketUpdateRequest) => {
    await updateTicket({
      path: { pteam_id: pteamId, ticket_id: ticket.ticket_id },
      body: requestData,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar(t("changeSucceeded"), { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(t("operationFailed", { error: errorToString(error) }), {
          variant: "error",
        }),
      );
  };

  const handleSave = async (
    safetyImpact: SafetyImpactEnum | null,
    ticketSafetyImpactChangeReason: string,
  ) => {
    const requestData: TicketUpdateRequest = {
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
