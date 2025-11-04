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

import { usePTeamServiceDetailsData } from "../../../hooks/Status/usePTeamServiceDetailsData";
import { PTeamServiceDetailsSettings } from "../ServiceDetailsSettings/PTeamServiceDetailsSettings";

export function PTeamServiceDetailsMobile(props) {
  const { image, serviceName, description, keywords, statusItems } = usePTeamServiceDetailsData(
    props.pteamId,
    props.service,
    props.highestSsvcPriority,
  );

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
      }}
    >
      <Card sx={{ width: "100%", maxWidth: { xs: 320, sm: 400 } }}>
        <CardMedia component="img" image={image} sx={{ aspectRatio: "4 / 3" }} />
        <CardContent>
          <Stack direction="row" spacing={1} useFlexGap sx={{ mb: 1, flexWrap: "wrap" }}>
            {keywords.map((keyword) => (
              <Chip key={keyword} label={keyword} size="small" />
            ))}
          </Stack>
          <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
            <Typography
              variant="h6"
              noWrap
              sx={{
                minWidth: 0,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
              title={serviceName}
            >
              {serviceName}
            </Typography>
            <PTeamServiceDetailsSettings
              pteamId={props.pteamId}
              service={props.service}
              expandService={true}
            />
          </Box>
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
