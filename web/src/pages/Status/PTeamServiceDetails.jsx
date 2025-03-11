import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  Box,
  Button,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Collapse,
  Divider,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { useGetPTeamServiceThumbnailQuery } from "../../services/tcApi";

import { PTeamStatusSSVCCards } from "./PTeamStatusSSVCCards";
import { PTeamServiceDetailsSettings } from "./ServiceDetailsSettings/PTeamServiceDetailsSettings";

const noImageAvailableUrl = "images/no-image-available-720x480.png";

function ServiceIDCopyButton({ ServiceId }) {
  const defaultMessage = "Copy the Service ID";
  const defaultPosition = "bottom";

  const [tooltipText, setTooltipText] = useState(defaultMessage);
  const [tooltipPlacement, setTooltipPlacement] = useState(defaultPosition);

  // change the message when clicked
  const handleClick = () => {
    setTooltipText("Copied");
    setTooltipPlacement("top");
  };

  // reset the tooltip state when completed
  const handleClose = () => {
    if (tooltipText === "Copied") {
      setTooltipText(defaultMessage);
      setTooltipPlacement(defaultPosition);
    }
  };

  return (
    <>
      <Tooltip title={tooltipText} placement={tooltipPlacement} onClose={handleClose}>
        <IconButton
          color="primary"
          aria-label="copy-id"
          onClick={() => {
            navigator.clipboard.writeText(ServiceId);
            handleClick();
          }}
        >
          <InfoOutlinedIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </>
  );
}

ServiceIDCopyButton.propTypes = {
  ServiceId: PropTypes.oneOfType([PropTypes.string, PropTypes.element]).isRequired,
};

export function PTeamServiceDetails(props) {
  const { pteamId, service, expandService, onSwitchExpandService, highestSsvcPriority } = props;

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

  return (
    <>
      <Collapse
        in={expandService}
        collapsedSize={100}
        sx={
          expandService
            ? {}
            : {
                position: "relative",
                "&::before": {
                  content: "''",
                  width: "100%",
                  height: "100%",
                  display: "block",
                  background: "linear-gradient(rgba(255,255,255,0) 0, #fff 80%)",
                  position: "absolute",
                  zIndex: 10,
                },
              }
        }
      >
        <Card sx={{ display: "flex", height: 200, position: "relative" }}>
          <PTeamServiceDetailsSettings pteamId={pteamId} service={service} />
          <CardMedia image={image} sx={{ aspectRatio: "4 / 3" }} />
          <Divider orientation="vertical" variant="middle" flexItem />
          <CardContent sx={{ flex: 1 }}>
            <Stack direction="row" spacing={1}>
              {keywords.map((keyword) => (
                <Chip key={keyword} label={keyword} size="small" />
              ))}
            </Stack>
            <Typography variant="h5">
              {serviceName}
              <ServiceIDCopyButton ServiceId={service.service_id} />
            </Typography>
            <Typography variant="body2" sx={{ wordBreak: "break-all" }}>
              {description}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              {`Default safety impact: ${service.service_safety_impact}`}
            </Typography>
          </CardContent>
        </Card>
        <Box sx={{ mt: 1 }}>
          <PTeamStatusSSVCCards
            pteamId={pteamId}
            service={service}
            highestSsvcPriority={highestSsvcPriority}
          />
        </Box>
      </Collapse>
      <Button onClick={onSwitchExpandService} sx={{ display: "block", m: "auto" }}>
        {expandService ? "- READ LESS" : "+ READ MORE"}
      </Button>
    </>
  );
}

PTeamServiceDetails.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
  expandService: PropTypes.bool.isRequired,
  onSwitchExpandService: PropTypes.func.isRequired,
  highestSsvcPriority: PropTypes.string.isRequired,
};
