import { useGetPTeamServiceThumbnailQuery } from "../../services/tcApi";
import { systemExposure, missionImpact } from "../../utils/const";
import { ssvcPriorityProps } from "../../utils/ssvcUtils";
import { useTranslation } from "react-i18next";

const noImageAvailableUrl = "images/no-image-available-720x480.png";

export function usePTeamServiceDetailsData(pteamId, service, highestSsvcPriority) {
  const { t } = useTranslation("hooks", { keyPrefix: "PTeamServiceDetails.labels" });
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
      label: t("highestSsvcPriority"),
      value: ssvcPriorityProps[highestSsvcPriority]?.displayName || highestSsvcPriority,
    },
    {
      label: t("systemExposure"),
      value: systemExposure[service.system_exposure] || service.system_exposure,
    },
    {
      label: t("missionImpact"),
      value: missionImpact[service.service_mission_impact] || service.service_mission_impact,
    },
    { label: t("defaultSafetyImpact"), value: service.service_safety_impact },
  ];

  return {
    image,
    serviceName: service.service_name,
    description: service.description,
    keywords: service.keywords,
    statusItems,
  };
}
