import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useGetThreatQuery, useUpdateThreatMutation } from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";

import { SafetyImpactSelectorView } from "./SafetyImpactSelectorView";

export function SafetyImpactSelector(props) {
  const { threatId } = props;

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: threat,
    error: threatError,
    isLoading: threatIsLoading,
  } = useGetThreatQuery(threatId, { skip });

  const [updateThreat] = useUpdateThreatMutation();

  const { enqueueSnackbar } = useSnackbar();

  if (skip) return <></>;
  if (threatError) throw new APIError(errorToString(threatError), { api: "getThreat" });
  if (threatIsLoading) return <>Now loading Threat...</>;

  const updateThreatFunction = async (requestData) => {
    await updateThreat({
      threatId,
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

  return (
    <SafetyImpactSelectorView
      threatSafetyImpact={threat.threat_safety_impact}
      reasonSafetyImpact={threat.reason_safety_impact}
      updateThreatFunction={updateThreatFunction}
    />
  );
}
SafetyImpactSelector.propTypes = {
  threatId: PropTypes.string.isRequired,
};
