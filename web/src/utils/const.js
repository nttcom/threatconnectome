import CheckIcon from "@mui/icons-material/Check";
import HealthAndSafetyIcon from "@mui/icons-material/HealthAndSafety";
import PriorityHighIcon from "@mui/icons-material/PriorityHigh";
import RunningWithErrorsIcon from "@mui/icons-material/RunningWithErrors";
import WarningIcon from "@mui/icons-material/Warning";
import {
  amber,
  blueGrey,
  brown,
  green,
  grey,
  lightBlue,
  orange,
  red,
  teal,
  yellow,
} from "@mui/material/colors";

export const rootPrefix = process.env.PUBLIC_URL.replace(/\/+$/, ""); // trim trailing slash

export const systemAccount = {
  uuid: "00000000-0000-0000-0000-0000cafe0011",
  email: process.env.REACT_APP_SYSTEM_EMAIL || "SYSTEM_ACCOUNT",
};

export const actionTypeChipWidth = 90;

export const drawerWidth = 200;

export const mainMaxWidth = 1100;

export const actionTypeChipColors = {
  elimination: "error",
  mitigation: "warning",
  detection: "success",
  transfer: "info",
  acceptance: "primary",
  rejection: "secondary",
};
export const actionTypes = Object.keys(actionTypeChipColors);

export const experienceColors = {
  0: green[500],
  2: yellow[500],
  5: orange[500],
  7: red[500],
};

export const threatImpactNames = {
  1: "immediate",
  2: "offcycle",
  3: "acceptable",
  4: "none",
};

export const threatImpactProps = {
  immediate: {
    chipLabel: "Immediate",
    icon: RunningWithErrorsIcon,
    statusLabel: "Your pteam has a immediate",
    style: {
      bgcolor: red[600],
      color: "white",
      textTransform: "none",
    },
  },
  offcycle: {
    chipLabel: "Off-cycle",
    icon: WarningIcon,
    statusLabel: "Your pteam has a off-cycle",
    style: {
      bgcolor: orange[600],
      color: "white",
      textTransform: "none",
    },
  },
  acceptable: {
    chipLabel: "Acceptable",
    icon: PriorityHighIcon,
    statusLabel: "Your pteam has a acceptable",
    style: {
      bgcolor: amber[600],
      color: "white",
      textTransform: "none",
    },
  },
  none: {
    chipLabel: "None",
    icon: CheckIcon,
    statusLabel: "Your pteam has none",
    style: {
      bgcolor: grey[600],
      color: "white",
      textTransform: "none",
    },
  },
  safe: {
    chipLabel: "Safe",
    icon: HealthAndSafetyIcon,
    statusLabel: "Your pteam has safe",
    style: {
      bgcolor: green[600],
      color: "white",
      textTransform: "none",
    },
  },
};

const prop_immediate = {
  displayName: "Immediate",
  icon: RunningWithErrorsIcon,
  statusLabel:
    "Immediate: Act immediately; focus all resources on applying the fix as quickly as possible, including, if necessary, pausing regular organization operations.",
  style: {
    bgcolor: red[600],
    color: "white",
    textTransform: "none",
  },
};
const prop_out_of_cycle = {
  displayName: "Out-of-cycle",
  icon: WarningIcon,
  statusLabel:
    "Out-of-cycle: Act more quickly than usual to apply the mitigation or remediation out-of-cycle, during the next available opportunity, working overtime if necessary.",
  style: {
    bgcolor: orange[600],
    color: "white",
    textTransform: "none",
  },
};
const prop_scheduled = {
  displayName: "Scheduled",
  icon: PriorityHighIcon,
  statusLabel: "Scheduled: Act during regularly scheduled maintenance time.",
  style: {
    bgcolor: amber[600],
    color: "white",
    textTransform: "none",
  },
};
const prop_defer = {
  displayName: "Defer",
  icon: CheckIcon,
  statusLabel: "Defer: Do not act at present.",
  style: {
    bgcolor: grey[600],
    color: "white",
    textTransform: "none",
  },
};
const prop_safe = {
  chipLabel: "Safe",
  icon: HealthAndSafetyIcon,
  statusLabel: "All vulnerabilities have been resolved",
  style: {
    bgcolor: green[600],
    color: "white",
    textTransform: "none",
  },
};
// sorted priorities -- should match with strings which api returns.
export const sortedSSVCPriorities = ["immediate", "out_of_cycle", "scheduled", "defer"];
export const ssvcPriorityProps = {
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
export const defaultAlertThreshold = sortedSSVCPriorities[0];

export const sortedSystemExposure = ["open", "controlled", "small"];
export const systemExposure = {
  open: "Open",
  controlled: "Controlled",
  small: "Small",
};

export const sortedMissionImpat = [
  "mission_failure",
  "mef_failure",
  "mef_support_crippled",
  "degraded",
];
export const missionImpact = {
  mission_failure: "Mission Failure",
  mef_failure: "MEF Failure",
  mef_support_crippled: "MEF Support Crippled",
  degraded: "Degraded",
};

/* Safety Impact */
export const safetyImpactDescription =
  "The safety impact of the vulnerability. (based on IEC 61508)";
export const sortedSafetyImpacts = [
  // should match with strings which api returns
  "catastrophic",
  "critical",
  "marginal",
  "negligible",
];
const propSafetyImpactCatastrophic = {
  displayName: "Catastrophic",
};
const propSafetyImpactCritical = {
  displayName: "Critical",
};
const propSafetyImpactMarginal = {
  displayName: "Marginal",
};
const propSafetyImpactNegligible = {
  displayName: "Negligible",
};
export const safetyImpactProps = {
  catastrophic: propSafetyImpactCatastrophic,
  Catastrophic: propSafetyImpactCatastrophic,
  critical: propSafetyImpactCritical,
  Critical: propSafetyImpactCritical,
  marginal: propSafetyImpactMarginal,
  Marginal: propSafetyImpactMarginal,
  negligible: propSafetyImpactNegligible,
  Negligible: propSafetyImpactNegligible,
};

export const sortedTopicStatus = ["alerted", "acknowledged", "scheduled", "completed"];
export const topicStatusProps = {
  alerted: {
    chipLabel: "alerted",
    chipLabelCapitalized: "Alerted",
    style: {
      bgcolor: teal[50],
      color: "red",
    },
    buttonStyle: {
      color: blueGrey[700],
      "&:hover": {
        bgcolor: blueGrey[50],
      },
    },
  },
  acknowledged: {
    chipLabel: "acknowledged",
    chipLabelCapitalized: "Acknowledged",
    style: {
      bgcolor: teal[200],
      color: "black",
    },
    buttonStyle: {
      color: lightBlue[700],
      "&:hover": {
        bgcolor: lightBlue[50],
      },
    },
  },
  scheduled: {
    chipLabel: "scheduled",
    chipLabelCapitalized: "Scheduled",
    style: {
      bgcolor: teal[600],
      color: "white",
    },
    buttonStyle: {
      color: teal[700],
      "&:hover": {
        bgcolor: teal[50],
      },
    },
  },
  completed: {
    chipLabel: "completed",
    chipLabelCapitalized: "Completed",
    style: {
      bgcolor: green[600],
      color: "white",
    },
    buttonStyle: {
      color: green[700],
      "&:hover": {
        bgcolor: green[50],
      },
    },
  },
};

export const commonButtonStyle = {
  bgcolor: green[700],
  color: "white",
  textTransform: "none",
  "&:hover": {
    bgcolor: green[900],
  },
};

export const cancelButtonStyle = {
  color: grey[900],
  "&:hover": {
    bgcolor: grey[100],
  },
};

export const modalCommonButtonStyle = {
  color: "inherit",
  textTransform: "none",
  "&:hover": {
    bgcolor: grey[100],
  },
};

export const sxModal = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  maxHeight: "90%",
  overflow: "auto",
  bgcolor: "background.paper",
  boxShadow: 24,
  p: 4,
};

export const noPTeamMessage = "You do not belong to any pteam. Please create a pteam.";

export const drawerParams = {
  mainColor: brown[900],
  hoverColor: brown[700],
};

export const cvssProps = {
  None: {
    cvssBgcolor: grey[600],
    threatCardBgcolor: grey[100],
  },
  Low: {
    cvssBgcolor: amber[600],
    threatCardBgcolor: amber[100],
  },
  Medium: {
    cvssBgcolor: amber[600],
    threatCardBgcolor: amber[100],
  },
  High: {
    cvssBgcolor: orange[600],
    threatCardBgcolor: orange[100],
  },
  Critical: {
    cvssBgcolor: red[600],
    threatCardBgcolor: red[100],
  },
};
