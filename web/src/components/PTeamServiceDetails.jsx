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
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { storeServiceThumbnail } from "../slices/pteam";
import { getServiceThumbnail } from "../utils/api";
import { blobToDataURL } from "../utils/func";

import { PTeamStatusSSVCCards } from "./PTeamStatusSSVCCards";

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

  const dispatch = useDispatch();

  const thumbnails = useSelector((state) => state.pteam.serviceThumbnails);

  const [image, setImage] = useState(noImageAvailableUrl);

  const thumbnail = thumbnails[service.service_id];
  const serviceName = service.service_name;
  const description = service.description;
  const keywords = service.keywords;

  useEffect(() => {
    if (thumbnail === undefined) {
      getServiceThumbnail(pteamId, service.service_id)
        .then(async (response) => {
          const dataUrl = await blobToDataURL(response.data);
          dispatch(storeServiceThumbnail({ serviceId: service.service_id, data: dataUrl }));
        })
        .catch((error) => {
          dispatch(
            storeServiceThumbnail({ serviceId: service.service_id, data: noImageAvailableUrl }),
          );
        });
    }
  }, [pteamId, service.service_id, thumbnail, dispatch]);

  useEffect(() => {
    if (thumbnail !== undefined && image !== thumbnail) {
      setImage(thumbnail);
    }
  }, [thumbnail, image]);

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
                },
              }
        }
      >
        <Card sx={{ display: "flex", height: 200 }}>
          <CardMedia image={image} sx={{ aspectRatio: "4 / 3" }} />
          <Divider orientation="vertical" variant="middle" flexItem />
          <CardContent sx={{ flex: 1 }}>
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
              {keywords.map((keyword) => (
                <Chip key={keyword} label={keyword} size="small" />
              ))}
            </Stack>
            <Typography gutterBottom variant="h5">
              {serviceName}
              <ServiceIDCopyButton ServiceId={service.service_id} />
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ wordBreak: "break-all" }}>
              {description}
            </Typography>
          </CardContent>
        </Card>
        <Box sx={{ mt: 1 }}>
          <PTeamStatusSSVCCards service={service} highestSsvcPriority={highestSsvcPriority} />
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
