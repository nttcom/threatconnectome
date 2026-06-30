import type {
  RelatedTicketStatus,
  ServiceEntry,
  SsvcDeployerPackagePriorityEnum,
  TicketResponse,
} from "../../../types/types.gen";
import type { SxProps, Theme } from "@mui/material/styles";

export type PackageReference = {
  dependencyId: string;
  target: string;
  version: string;
  service: string;
  package_name: string;
  package_source_name?: string | null;
  package_manager: string;
  ecosystem: string;
};

export type PackageReferenceService = Pick<ServiceEntry, "service_name">;

export type TicketIdProps = {
  ticketId: string;
};

export type OptionalTicketIdProps = {
  ticketId?: string | null;
};

export type TicketSelectHandler = (ticketId: string) => void;

export type PackagePageParams = {
  pteamId: string;
  serviceId: string;
  packageVersionId: string;
};

export type TicketSectionStatus = "alerted" | "in-progress" | "completed";

export type MobileDialogView = "list" | "info" | "ticket";

export type SSVCPriorityKey = SsvcDeployerPackagePriorityEnum;

export type SSVCPriorityCountChipProps = {
  ssvcPriority: SSVCPriorityKey;
  count: number;
  reverse?: boolean;
  sx?: SxProps<Theme>;
  outerSx?: SxProps<Theme>;
};

export type VulnerabilityTableProps = {
  relatedTicketStatus: RelatedTicketStatus;
};

export type TicketListItemProps = {
  ticket: TicketResponse;
  isSelected: boolean;
  onSelect: TicketSelectHandler;
};
