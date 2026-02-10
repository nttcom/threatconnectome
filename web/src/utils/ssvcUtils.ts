import CheckIcon from "@mui/icons-material/Check";
import HealthAndSafetyIcon from "@mui/icons-material/HealthAndSafety";
import PriorityHighIcon from "@mui/icons-material/PriorityHigh";
import RunningWithErrorsIcon from "@mui/icons-material/RunningWithErrors";
import WarningIcon from "@mui/icons-material/Warning";
import { amber, green, grey, orange, red } from "@mui/material/colors";
import i18n from "i18next";

import { TicketResponse } from "../../types/types.gen";

export const sortedSSVCPriorities = ["immediate", "out_of_cycle", "scheduled", "defer"];

export const getSsvcPriorityProps = () => {
  const prop_immediate = {
    displayName: i18n.t("ssvcUtils.priority.immediate.displayName", { ns: "utils" }),
    icon: RunningWithErrorsIcon,
    statusLabel: i18n.t("ssvcUtils.priority.immediate.statusLabel", { ns: "utils" }),
    style: {
      bgcolor: red[600],
      color: "white",
      textTransform: "none",
    },
  };
  const prop_out_of_cycle = {
    displayName: i18n.t("ssvcUtils.priority.out_of_cycle.displayName", { ns: "utils" }),
    icon: WarningIcon,
    statusLabel: i18n.t("ssvcUtils.priority.out_of_cycle.statusLabel", { ns: "utils" }),
    style: {
      bgcolor: orange[600],
      color: "white",
      textTransform: "none",
    },
  };
  const prop_scheduled = {
    displayName: i18n.t("ssvcUtils.priority.scheduled.displayName", { ns: "utils" }),
    icon: PriorityHighIcon,
    statusLabel: i18n.t("ssvcUtils.priority.scheduled.statusLabel", { ns: "utils" }),
    style: {
      bgcolor: amber[600],
      color: "white",
      textTransform: "none",
    },
  };
  const prop_defer = {
    displayName: i18n.t("ssvcUtils.priority.defer.displayName", { ns: "utils" }),
    icon: CheckIcon,
    statusLabel: i18n.t("ssvcUtils.priority.defer.statusLabel", { ns: "utils" }),
    style: {
      bgcolor: grey[600],
      color: "white",
      textTransform: "none",
    },
  };
  const prop_safe = {
    chipLabel: i18n.t("ssvcUtils.priority.safe.chipLabel", { ns: "utils" }),
    icon: HealthAndSafetyIcon,
    statusLabel: i18n.t("ssvcUtils.priority.safe.statusLabel", { ns: "utils" }),
    style: {
      bgcolor: green[600],
      color: "white",
      textTransform: "none",
    },
  };
  return {
    immediate: prop_immediate,
    Immediate: prop_immediate,
    out_of_cycle: prop_out_of_cycle,
    "Out-of-cycle": prop_out_of_cycle,
    scheduled: prop_scheduled,
    Scheduled: prop_scheduled,
    defer: prop_defer,
    Defer: prop_defer,
    safe: prop_safe,
    Safe: prop_safe,
    empty: prop_defer,
    Empty: prop_defer,
  };
};

type SSVCPriority =
  | "immediate"
  | "Immediate"
  | "out_of_cycle"
  | "Out-of-cycle"
  | "scheduled"
  | "Scheduled"
  | "defer"
  | "Defer"
  | "safe"
  | "Safe"
  | "empty"
  | "Empty";

export const compareSSVCPriority = (prio1: SSVCPriority, prio2: SSVCPriority) => {
  const toIntDict = {
    immediate: 1,
    Immediate: 1,
    out_of_cycle: 2,
    "Out-of-cycle": 2,
    scheduled: 3,
    Scheduled: 3,
    defer: 4,
    Defer: 4,
    safe: 4,
    Safe: 4,
    empty: 4,
    Empty: 4,
  };
  const [int1, int2] = [toIntDict[prio1], toIntDict[prio2]];
  if (int1 === int2) return 0;
  else if (int1 < int2) return -1;
  else return 1;
};

export const searchWorstSSVC = (tickets: Array<TicketResponse>) => {
  if (!tickets || tickets.length === 0) {
    return null;
  }

  const result = tickets.reduce((worstSSVC, ticket) => {
    const currentPrio = ticket.ssvc_deployer_priority ?? "empty";
    const worstPrio = worstSSVC ?? "empty";
    if (compareSSVCPriority(worstPrio, currentPrio) === 1) {
      return ticket.ssvc_deployer_priority;
    }
    return worstSSVC;
  }, tickets[0].ssvc_deployer_priority);

  return result;
};

export const getSsvcColor = (ssvc: string | null | undefined) => {
  if (!ssvc) return undefined;

  const lowerSsvc = ssvc.toLowerCase();

  switch (lowerSsvc) {
    case "immediate":
      return "error";
    case "out_of_cycle":
    case "out-of-cycle":
      return "warning";
    case "scheduled":
      return "info";
    case "defer":
      return "default";
    default:
      return undefined;
  }
};
