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
import React, { useState } from "react";

export const PTeamServiceDetails = () => {
  const [isOpen, setIsOpen] = useState(false);
  const image = "./images/PXL_20240716_072606176.jpg";
  const serviceName = "service_name";
  const description =
    "Lizards are a widespread group of squamate reptiles, with over 6,000 species, ranging across all continents except Antarctica";
  const labelList = ["Chip", "Label", "Looooooooooooooong label"];

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
          <CardMedia component="img" image={image} sx={{ width: 300 }} />
          <CardContent>
            <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
              {labelList.map((label) => (
                <Chip key={label} label={label} size="small" />
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
};
