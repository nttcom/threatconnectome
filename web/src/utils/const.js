import CheckIcon from "@mui/icons-material/Check";
import HealthAndSafetyIcon from "@mui/icons-material/HealthAndSafety";
import PriorityHighIcon from "@mui/icons-material/PriorityHigh";
import RunningWithErrorsIcon from "@mui/icons-material/RunningWithErrors";
import WarningIcon from "@mui/icons-material/Warning";
import {
  amber,
  blue,
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

export const difficulty = ["high", "middle", "low"];

export const difficultyColors = {
  low: amber[500],
  middle: yellow[700],
  high: red[500],
};

export const avatarGroupStyle = {
  alignItems: "center",
  "& .MuiAvatarGroup-avatar": {
    border: `2px solid ${grey[400]}`,
    height: "33px",
    width: "33px",
    "&.low": {
      border: `2px solid ${difficultyColors.low}`,
    },
    "&.middle": {
      border: `2px solid ${difficultyColors.middle}`,
    },
    "&.high": {
      border: `2px solid ${difficultyColors.high}`,
    },
  },
};

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
  statusLabel: "Your pteam has a immediate",
  style: {
    bgcolor: red[600],
    color: "white",
    textTransform: "none",
  },
};
const prop_out_of_cycle = {
  displayName: "Out-of-cycle",
  icon: WarningIcon,
  statusLabel: "Your pteam has a out-of-cycle",
  style: {
    bgcolor: orange[600],
    color: "white",
    textTransform: "none",
  },
};
const prop_scheduled = {
  displayName: "Scheduled",
  icon: PriorityHighIcon,
  statusLabel: "Your pteam has a scheduled",
  style: {
    bgcolor: amber[600],
    color: "white",
    textTransform: "none",
  },
};
const prop_defer = {
  displayName: "Defer",
  icon: CheckIcon,
  statusLabel: "Your pteam has defer",
  style: {
    bgcolor: grey[600],
    color: "white",
    textTransform: "none",
  },
};
const prop_safe = {
  chipLabel: "Safe",
  icon: HealthAndSafetyIcon,
  statusLabel: "Your pteam has safe",
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
};

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
export const noATeamMessage = "You do not belong to any ateam. Please create an ateam.";

export const teamColor = {
  pteam: {
    mainColor: brown[900],
    hoverColor: brown[700],
  },
  ateam: {
    mainColor: blue[900],
    hoverColor: blue[700],
  },
};
