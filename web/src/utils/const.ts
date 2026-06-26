import { blueGrey, green, grey, lightBlue, orange, red, teal, yellow } from "@mui/material/colors";
import { t } from "i18next";

export const mainMaxWidth = 1100;

export const maxReasonSafetyImpactLengthInHalf = 2000;
export const maxServiceNameLengthInHalf = 255;
export const maxDescriptionLengthInHalf = 300;
export const maxAssetAddressLengthInHalf = 255;
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

export type ExperienceBucket = 0 | 2 | 5 | 7;

export const getExperienceBucket = (years: number): ExperienceBucket => {
  if (years >= 7) return 7;
  if (years >= 5) return 5;
  if (years >= 2) return 2;
  return 0;
};

/* Safety Impact */
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

export const sortedTicketHandlingStatus = ["alerted", "acknowledged", "scheduled", "completed"];
export const ticketHandlingStatusProps = {
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

export const getNoPTeamMessage = () => t("const.noPTeamMessage", { ns: "utils" });

export const preserveKeys = [
  "pteamId", // Query parameters required on all pages
  "serviceId", // Query parameters required on all pages
  "related", // Toggle button on Vulns Page
  "mytasks", // Toggle button on ToDo Page
];
