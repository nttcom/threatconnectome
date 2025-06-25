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

  // ステータスの表示用
  const highestPriorityLabel =
    ssvcPriorityProps[highestSsvcPriority]?.displayName || highestSsvcPriority;
  const systemExposureLabel = systemExposure[service.system_exposure] || service.system_exposure;
  const missionImpactLabel =
    missionImpact[service.service_mission_impact] || service.service_mission_impact;

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
            <ListItem disableGutters sx={{ py: 0 }}>
              <Stack direction="row" spacing={2} sx={{ width: "100%" }}>
                <Typography variant="body2" sx={{ minWidth: 140, fontWeight: "bold" }}>
                  Highest SSVC Priority
                </Typography>
                <Typography variant="body2">{highestPriorityLabel}</Typography>
              </Stack>
            </ListItem>
            <ListItem disableGutters sx={{ py: 0 }}>
              <Stack direction="row" spacing={2} sx={{ width: "100%" }}>
                <Typography variant="body2" sx={{ minWidth: 140, fontWeight: "bold" }}>
                  System Exposure
                </Typography>
                <Typography variant="body2">{systemExposureLabel}</Typography>
              </Stack>
            </ListItem>
            <ListItem disableGutters sx={{ py: 0 }}>
              <Stack direction="row" spacing={2} sx={{ width: "100%" }}>
                <Typography variant="body2" sx={{ minWidth: 140, fontWeight: "bold" }}>
                  Mission Impact
                </Typography>
                <Typography variant="body2">{missionImpactLabel}</Typography>
              </Stack>
            </ListItem>
            <ListItem disableGutters sx={{ py: 0 }}>
              <Stack direction="row" spacing={2} sx={{ width: "100%" }}>
                <Typography variant="body2" sx={{ minWidth: 140, fontWeight: "bold" }}>
                  Default Safety Impact
                </Typography>
                <Typography variant="body2">{service.service_safety_impact}</Typography>
              </Stack>
            </ListItem>
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
