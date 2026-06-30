import type { Dispatch, SetStateAction } from "react";

import type {
  MissionImpactEnum,
  SsvcDeployerPackagePriorityEnum,
  SystemExposureEnum,
} from "../../../../types/types.gen";

export type SbomServiceTab = {
  id: string;
  title: string;
};

export type SbomService = SbomServiceTab & {
  address: string;
  countryCode: string;
  description: string;
  imageUrl: string;
  ipAddresses: string[];
  missionImpact: MissionImpactEnum;
  systemExposure: SystemExposureEnum;
  tags: string[];
};

export type SbomServicePatch = Partial<
  Pick<
    SbomService,
    | "address"
    | "countryCode"
    | "description"
    | "ipAddresses"
    | "missionImpact"
    | "systemExposure"
    | "tags"
    | "title"
  >
>;

export type SbomDependency = {
  license: string;
  name: string;
  packageVersionId?: string;
  serviceId?: string;
  ssvcPriority: SsvcDeployerPackagePriorityEnum;
  type: string;
  version: string;
};

export type PendingThumbnail = {
  deleted: boolean;
  file: File | null;
  previewDataUrl: string | null;
};

export type PendingUpload = {
  initialFile?: File;
  serviceName?: string;
};

export type OnActiveIdChange = (serviceId: string) => void;

export type OnPackageClick = (serviceId: string, packageVersionId: string) => void;

export type SetNumberState = Dispatch<SetStateAction<number>>;
