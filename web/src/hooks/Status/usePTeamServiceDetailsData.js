import { useGetPTeamServiceThumbnailQuery } from "../../services/tcApi";
import { systemExposure, missionImpact } from "../../utils/const";
import { ssvcPriorityProps } from "../../utils/ssvcUtils";

const noImageAvailableUrl = "images/no-image-available-720x480.png";

export function usePTeamServiceDetailsData(pteamId, service, highestSsvcPriority) {
  const {
    data: thumbnail,
    isError: thumbnailIsError,
    isLoading: thumbnailIsLoading,
  } = useGetPTeamServiceThumbnailQuery({
    path: { pteam_id: pteamId, service_id: service.service_id },
  });

  const image =
    thumbnailIsError || thumbnailIsLoading || !thumbnail ? noImageAvailableUrl : thumbnail;

  const statusItems = [
    {
      label: "Highest SSVC Priority",
      value: ssvcPriorityProps[highestSsvcPriority]?.displayName || highestSsvcPriority,
    },
    {
      label: "System Exposure",
      value: systemExposure[service.system_exposure] || service.system_exposure,
    },
    {
      label: "Mission Impact",
      value: missionImpact[service.service_mission_impact] || service.service_mission_impact,
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
