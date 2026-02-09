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
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { usePTeamServiceDetailsData } from "../../../hooks/Status/usePTeamServiceDetailsData";
import { PTeamStatusSSVCCards } from "../PTeamStatusSSVCCards";
import { PTeamServiceDetailsSettings } from "../ServiceDetailsSettings/PTeamServiceDetailsSettings";

function ServiceIDCopyButton({ ServiceId }) {
  const { t } = useTranslation("status", { keyPrefix: "ServiceIDCopyButton" });
  const defaultMessage = t("copyServiceId");
  const defaultPosition = "bottom";

  const [tooltipText, setTooltipText] = useState(defaultMessage);
  const [tooltipPlacement, setTooltipPlacement] = useState(defaultPosition);

  // change the message when clicked
  const handleClick = () => {
    setTooltipText(t("copied"));
    setTooltipPlacement("top");
  };

  // reset the tooltip state when completed
  const handleClose = () => {
    if (tooltipText === t("copied")) {
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

  const { image, serviceName, description, keywords } = usePTeamServiceDetailsData(
    props.pteamId,
    props.service,
    props.highestSsvcPriority,
  );

  const handleCollapseClick = () => {
    if (!expandService) {
      onSwitchExpandService();
    }
  };

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
                cursor: "pointer",
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
        onClick={handleCollapseClick}
      >
        <Card sx={{ display: "flex", height: 200, position: "relative" }}>
          <PTeamServiceDetailsSettings
            pteamId={pteamId}
            service={service}
            expandService={expandService}
          />
          <CardMedia image={image} sx={{ aspectRatio: "4 / 3" }} />
          <Divider orientation="vertical" variant="middle" flexItem />
          <CardContent sx={{ display: "flex", flex: 1, minWidth: 0 }}>
            <Box sx={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
              <Stack
                direction="row"
                spacing={0.5}
                useFlexGap
                sx={{
                  maxWidth: "90%", // Limit width to 90% to avoid overlapping with the absolutely positioned settings button.
                  flexWrap: "wrap",
                }}
              >
                {keywords.map((keyword) => (
                  <Chip key={keyword} label={keyword} size="small" />
                ))}
              </Stack>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <Box
                  sx={{
                    display: "flex",
                    minWidth: 0,
                    maxWidth: "90%", // Limit width to 90% to avoid overlapping with the absolutely positioned settings button.
                  }}
                >
                  <Typography
                    variant="h5"
                    sx={{
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                    title={serviceName}
                  >
                    {serviceName}
                  </Typography>
                  <ServiceIDCopyButton ServiceId={service.service_id} />
                </Box>
              </Box>
              <Typography variant="body2" sx={{ wordBreak: "break-all" }}>
                {description}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {`Default safety impact: ${service.service_safety_impact}`}
              </Typography>
            </Box>
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
