import type { PTeamServiceResponse } from "../../../types/types.gen";
import { useGetPTeamServiceThumbnailQuery } from "../../services/tcApi";
import { systemExposure, missionImpact } from "../../utils/const";
import { getSsvcPriorityProps } from "../../utils/ssvcUtils";

const noImageAvailableUrl = "images/no-image-available-720x480.png";

export type StatusItem = {
  label: string;
  value: string;
};

export type PTeamServiceDetailsData = {
  image: string;
  serviceName: string;
  description: string | null;
  keywords: string[];
  statusItems: StatusItem[];
};

export function usePTeamServiceDetailsData(
  pteamId: string,
  service: PTeamServiceResponse,
  highestSsvcPriority: string,
): PTeamServiceDetailsData {
  const {
    data: thumbnail,
    isError: thumbnailIsError,
    isLoading: thumbnailIsLoading,
  } = useGetPTeamServiceThumbnailQuery({
    path: { pteam_id: pteamId, service_id: service.service_id },
  });

  const image =
    thumbnailIsError || thumbnailIsLoading || !thumbnail ? noImageAvailableUrl : thumbnail;

  const ssvcProps = getSsvcPriorityProps() as Record<string, { displayName: string } | undefined>;
  const exposureMap = systemExposure as Record<string, string>;
  const missionMap = missionImpact as Record<string, string>;

  const statusItems: StatusItem[] = [
    {
      label: "Highest SSVC Priority",
      value: ssvcProps[highestSsvcPriority]?.displayName || highestSsvcPriority,
    },
    {
      label: "System Exposure",
      value: exposureMap[service.system_exposure] || service.system_exposure,
    },
    {
      label: "Mission Impact",
      value: missionMap[service.service_mission_impact] || service.service_mission_impact,
    },
    { label: "Default Safety Impact", value: service.service_safety_impact },
  ];

  return {
    image,
    serviceName: service.service_name,
    description: service.description,
    keywords: service.keywords,
    statusItems,
  };
}
