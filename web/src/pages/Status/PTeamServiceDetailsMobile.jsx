import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Stack,
  Typography,
  List,
  ListItem,
} from "@mui/material";
import PropTypes from "prop-types";

import { useGetPTeamServiceThumbnailQuery } from "../../services/tcApi";
import { ssvcPriorityProps, systemExposure, missionImpact } from "../../utils/const";

const noImageAvailableUrl = "images/no-image-available-720x480.png";

export function PTeamServiceDetailsMobile({ pteamId, service, highestSsvcPriority }) {
  const {
    data: thumbnail,
    isError: thumbnailIsError,
    isLoading: thumbnailIsLoading,
  } = useGetPTeamServiceThumbnailQuery({
    pteamId,
    serviceId: service.service_id,
  });

  const image =
    thumbnailIsError || thumbnailIsLoading || !thumbnail ? noImageAvailableUrl : thumbnail;
  const serviceName = service.service_name;
  const description = service.description;
  const keywords = service.keywords;

  const highestPriorityLabel =
    ssvcPriorityProps[highestSsvcPriority]?.displayName || highestSsvcPriority;
  const systemExposureLabel = systemExposure[service.system_exposure] || service.system_exposure;
  const missionImpactLabel =
    missionImpact[service.service_mission_impact] || service.service_mission_impact;

  const statusItems = [
    { label: "Highest SSVC Priority", value: highestPriorityLabel },
    { label: "System Exposure", value: systemExposureLabel },
    { label: "Mission Impact", value: missionImpactLabel },
    { label: "Default Safety Impact", value: service.service_safety_impact },
  ];

  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
      <Card sx={{ width: "100%", maxWidth: 400 }}>
        <CardMedia component="img" image={image} sx={{ aspectRatio: "4 / 3" }} />
        <CardContent>
          <Stack direction="row" spacing={1} useFlexGap sx={{ mb: 1, flexWrap: "wrap" }}>
            {keywords.map((keyword) => (
              <Chip key={keyword} label={keyword} size="small" />
            ))}
          </Stack>
          <Typography variant="h6" sx={{ mb: 1 }}>
            {serviceName}
          </Typography>
          <Typography variant="body2" sx={{ mb: 1, wordBreak: "break-all" }}>
            {description}
          </Typography>
          <List
            dense
            sx={{
              mx: "auto",
              width: "fit-content",
              minWidth: 0,
              px: 0,
            }}
          >
            {statusItems.map((item) => (
              <ListItem key={item.label} disableGutters sx={{ py: 0 }}>
                <Stack direction="row" spacing={2} sx={{ width: "100%" }}>
                  <Typography variant="body2" sx={{ minWidth: 140, fontWeight: "bold" }}>
                    {item.label}
                  </Typography>
                  <Typography variant="body2">{item.value}</Typography>
                </Stack>
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
}

PTeamServiceDetailsMobile.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
  highestSsvcPriority: PropTypes.string.isRequired,
};
