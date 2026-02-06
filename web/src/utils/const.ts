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
import i18n from "../i18n";

export const drawerWidth = 200;

export const mainMaxWidth = 1100;

export const maxReasonSafetyImpactLengthInHalf = 2000;
export const maxServiceNameLengthInHalf = 255;
export const maxDescriptionLengthInHalf = 300;
export const maxKeywordLengthInHalf = 20;
export const maxKeywords = 5;
export const maxPTeamNameLengthInHalf = 50;
export const maxContactInfoLengthInHalf = 255;
export const maxEmailAddressLengthInHalf = 255;
export const maxSlackWebhookUrlLengthInHalf = 255;
export const serviceImageWidthSize = 720;
export const serviceImageHeightSize = 480;
export const serviceImageMaxSize = 512 * 1024;

export const experienceColors = {
  0: green[500],
  2: yellow[500],
  5: orange[500],
  7: red[500],
};

export const sortedSystemExposure = ["open", "controlled", "small"];
export const getSystemExposure = () => ({
  open: i18n.t("utils:const.systemExposure.open"),
  controlled: i18n.t("utils:const.systemExposure.controlled"),
  small: i18n.t("utils:const.systemExposure.small"),
});

// Backward compatibility
export const systemExposure = getSystemExposure();

export const sortedMissionImpact = [
  "mission_failure",
  "mef_failure",
  "mef_support_crippled",
  "degraded",
];
export const getMissionImpact = () => ({
  mission_failure: i18n.t("utils:const.missionImpact.mission_failure"),
  mef_failure: i18n.t("utils:const.missionImpact.mef_failure"),
  mef_support_crippled: i18n.t("utils:const.missionImpact.mef_support_crippled"),
  degraded: i18n.t("utils:const.missionImpact.degraded"),
});

// Backward compatibility
export const missionImpact = getMissionImpact();

/* Safety Impact */
export const sortedSafetyImpacts = [
  // should match with strings which api returns
  "catastrophic",
  "critical",
  "marginal",
  "negligible",
];
export const getSafetyImpactProps = () => {
  const propSafetyImpactCatastrophic = {
    displayName: i18n.t("utils:const.safetyImpact.catastrophic"),
  };
  const propSafetyImpactCritical = {
    displayName: i18n.t("utils:const.safetyImpact.critical"),
  };
  const propSafetyImpactMarginal = {
    displayName: i18n.t("utils:const.safetyImpact.marginal"),
  };
  const propSafetyImpactNegligible = {
    displayName: i18n.t("utils:const.safetyImpact.negligible"),
  };
  return {
    catastrophic: propSafetyImpactCatastrophic,
    Catastrophic: propSafetyImpactCatastrophic,
    critical: propSafetyImpactCritical,
    Critical: propSafetyImpactCritical,
    marginal: propSafetyImpactMarginal,
    Marginal: propSafetyImpactMarginal,
    negligible: propSafetyImpactNegligible,
    Negligible: propSafetyImpactNegligible,
  };
};

// Backward compatibility
export const safetyImpactProps = getSafetyImpactProps();

export const sortedTicketHandlingStatus = ["alerted", "acknowledged", "scheduled", "completed"];
export const getTicketHandlingStatusProps = () => ({
  alerted: {
    chipLabel: "alerted",
    chipLabelCapitalized: i18n.t("utils:const.ticketHandlingStatus.alerted"),
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
    chipLabelCapitalized: i18n.t("utils:const.ticketHandlingStatus.acknowledged"),
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
    chipLabelCapitalized: i18n.t("utils:const.ticketHandlingStatus.scheduled"),
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
    chipLabelCapitalized: i18n.t("utils:const.ticketHandlingStatus.completed"),
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
});

// Backward compatibility
export const ticketHandlingStatusProps = getTicketHandlingStatusProps();

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

export const getNoPTeamMessage = () => i18n.t("utils:const.noPTeamMessage");

// Backward compatibility
export const noPTeamMessage = getNoPTeamMessage();

export const drawerParams = {
  mainColor: brown[900],
  hoverColor: brown[700],
};

export const preserveKeys = [
  "pteamId", // Query parameters required on all pages
  "serviceId", // Query parameters required on all pages
  "allservices", // Toggle Button on Status Page
  "related", // Toggle button on Vulns Page
  "mytasks", // Toggle button on ToDo Page
];
