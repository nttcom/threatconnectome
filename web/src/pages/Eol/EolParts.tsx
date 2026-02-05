import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from "@mui/icons-material";
import { Chip } from "@mui/material";

import { ServiceEntry } from "../../../types/types.gen.ts";

import { getStatusLabel, Status } from "../../utils/eolUtils.ts";

const statusConfig = {
  expired: {
    color: "error",
    icon: <ErrorIcon />,
  },
  warning: {
    color: "warning",
    icon: <WarningIcon />,
  },
  active: {
    color: "success",
    icon: <CheckCircleIcon />,
  },
  unknown: {
    color: "default",
    icon: undefined,
  },
} as const;

export const StatusBadge = ({ status }: { status: Status }) => {
  const config = statusConfig[status];
  return (
    <Chip icon={config.icon} label={getStatusLabel(status)} size="small" color={config.color} />
  );
};

export type EolVersionForUi = {
  product_name: string;
  product_category: string;
  eol_version_id: string;
  version: string;
  eol_from: string;
  updated_at: string;
  services: ServiceEntry[];
};
