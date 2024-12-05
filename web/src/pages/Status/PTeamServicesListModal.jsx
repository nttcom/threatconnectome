import {
  Close as CloseIcon,
  KeyboardDoubleArrowRight as KeyboardDoubleArrowRightIcon,
} from "@mui/icons-material";
import {
  Box,
  Card,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Typography,
  CardHeader,
  MenuItem,
  Pagination,
  Select,
  CardMedia,
  CardContent,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import { useSkipUntilAuthTokenIsReady } from "../../hooks/auth";
import { useGetPTeamServiceThumbnailQuery, useGetPTeamQuery } from "../../services/tcApi";
import { errorToString } from "../../utils/func";

const noImageAvailableUrl = "images/no-image-available-720x480.png";

function ServiceCard(props) {
  const { pteamId, service, onClickService } = props;

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

  return (
    <Card
      onClick={() => onClickService(service.service_id)}
      variant="outlined"
      sx={{
        margin: 1,
        width: "100%",
        backgroundColor: grey[200],
        "&:hover": { bgcolor: grey[100] },
        display: "flex",
        height: 200,
      }}
    >
      <CardMedia image={image} sx={{ aspectRatio: "4 / 3" }} />
      <CardContent sx={{ flex: 1 }}>
        <CardHeader title={service.service_name} sx={{ px: 0 }}></CardHeader>
        <Typography variant="body2" color="text.secondary" sx={{ wordBreak: "break-all" }}>
          {service.description}
        </Typography>
      </CardContent>
    </Card>
  );
}
ServiceCard.propTypes = {
  pteamId: PropTypes.string.isRequired,
  service: PropTypes.object.isRequired,
  onClickService: PropTypes.func.isRequired,
};

export function PTeamServicesListModal(props) {
  const { onSetShow, show, tagId, tagName, serviceIds } = props;
  const handleClose = () => onSetShow(false);

  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");

  const skip = useSkipUntilAuthTokenIsReady() || !pteamId;
  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, { skip });

  if (skip) return <></>;
  if (pteamError) return <>{`Cannot get PTeam: ${errorToString(pteamError)}`}</>;
  if (pteamIsLoading) return <>Now loading PTeam...</>;

  const targetServices = pteam.services
    .filter((service) => serviceIds.includes(service.service_id))
    .sort((a, b) => a.service_name.localeCompare(b.service_name));
  const pageServices = targetServices.slice(perPage * (page - 1), perPage * page);

  if (tagId === "") {
    return;
  }

  const paginationRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 2 }}>
      <Pagination
        shape="rounded"
        page={page}
        count={Math.ceil(targetServices.length / perPage)}
        onChange={(event, value) => setPage(value)}
      />
      <Select
        size="small"
        variant="standard"
        value={perPage}
        onChange={(event) => {
          setPerPage(event.target.value);
          setPage(1);
        }}
      >
        {[10, 20, 50, 100].map((num) => (
          <MenuItem key={num} value={num} sx={{ justifyContent: "flex-end" }}>
            <Typography variant="body2" sx={{ mt: 0.3 }}>
              {num} Rows
            </Typography>
          </MenuItem>
        ))}
      </Select>
      <Box flexGrow={1} />
    </Box>
  );

  const handleNavigateTag = (serviceId) => {
    for (let key of ["tagId", "impactFilter", "word", "perPage", "page", "allservices"]) {
      params.delete(key);
    }
    params.set("serviceId", serviceId);
    navigate(`/tags/${tagId}?${params.toString()}`);
  };

  return (
    <Dialog open={show} onClose={handleClose} fullWidth maxWidth="md">
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography variant="h6">Selected Artifact</Typography>
          <KeyboardDoubleArrowRightIcon sx={{ ml: 0.5, mr: 0.5 }} />
          <Typography variant="h5" flexGrow={1}>
            {tagName}
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box alignItems="center" display="flex" flexWrap="wrap" flexDirection="row" flexGrow={1}>
          {paginationRow}
          {pageServices.map((service) => (
            <ServiceCard
              key={service.service_id}
              pteamId={pteamId}
              service={service}
              onClickService={handleNavigateTag}
            />
          ))}
        </Box>
      </DialogContent>
    </Dialog>
  );
}
PTeamServicesListModal.propTypes = {
  onSetShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  tagId: PropTypes.string.isRequired,
  tagName: PropTypes.string.isRequired,
  serviceIds: PropTypes.arrayOf(PropTypes.string),
};
