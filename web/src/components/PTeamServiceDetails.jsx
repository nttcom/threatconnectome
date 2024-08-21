import {
  Button,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Collapse,
  Stack,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import { getServiceThumbnail } from "../utils/api";

export function PTeamServiceDetails(props) {
  const { pteamId, service } = props;

  const [isOpen, setIsOpen] = useState(false);
  const [imageUrl, setImageUrl] = useState(undefined);

  useEffect(() => {
    async function fixImageUrl(pteamId, serviceId) {
      await getServiceThumbnail(pteamId, serviceId)
        .then((response) => setImageUrl(URL.createObjectURL(response.data)))
        .catch((error) => setImageUrl(null));
    }

    fixImageUrl(pteamId, service.service_id);
  }, [pteamId, service.service_id]);

  const serviceName = service.service_name;
  const description = service.description;
  const keywords = service.keywords;

  return (
    <>
      <Collapse
        in={isOpen}
        collapsedSize={100}
        sx={
          isOpen
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
        <Card sx={{ display: "flex" }}>
          <CardMedia component="img" image={imageUrl} sx={{ width: 300 }} />
          <CardContent>
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
              {keywords.map((keyword) => (
                <Chip key={keyword} label={keyword} size="small" />
              ))}
            </Stack>
            <Typography gutterBottom variant="h5">
              {serviceName}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          </CardContent>
        </Card>
      </Collapse>
      <Button onClick={() => setIsOpen(!isOpen)} sx={{ display: "block", m: "auto" }}>
        {isOpen ? "- Read less" : "+ Read more"}
      </Button>
    </>
  );
}

PTeamServiceDetails.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
};
