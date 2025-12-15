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
  MenuItem,
  Pagination,
  Select,
  CardMedia,
  CardContent,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetPTeamServiceThumbnailQuery, useGetPTeamQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import { preserveParams } from "../../utils/urlUtils";

const noImageAvailableUrl = "images/no-image-available-720x480.png";

function ServiceCard(props) {
  const { pteamId, service, onClickService } = props;
  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

  const {
    data: thumbnail,
    isError: thumbnailIsError,
    isLoading: thumbnailIsLoading,
  } = useGetPTeamServiceThumbnailQuery({
    path: { pteam_id: pteamId, service_id: service.service_id },
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
        flexDirection: isMdDown ? "column" : "row",
        height: isMdDown ? "auto" : 200,
      }}
    >
      <CardMedia image={image} sx={{ aspectRatio: "4 / 3" }} />
      <CardContent sx={{ flex: 1, minWidth: 0 }}>
        <Typography
          gutterBottom
          variant="h5"
          component="div"
          noWrap
          title={service.service_name}
          sx={(theme) => ({
            width: "100%",
            overflow: "hidden",
            textOverflow: "ellipsis",
            display: "block",
            p: theme.spacing(0, 0, 1, 0),
          })}
        >
          {service.service_name}
        </Typography>
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
  const { onSetShow, show, packageId, packageName, serviceIds } = props;
  const handleClose = () => onSetShow(false);

  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");

  const skip = useSkipUntilAuthUserIsReady() || !pteamId;
  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery({ path: { pteam_id: pteamId } }, { skip });

  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

  if (skip) return <></>;
  if (pteamError)
    throw new APIError(errorToString(pteamError), {
      api: "getPTeam",
    });
  if (pteamIsLoading) return <>Now loading Team...</>;

  const targetServices = pteam.services
    .filter((service) => serviceIds.includes(service.service_id))
    .sort((a, b) => a.service_name.localeCompare(b.service_name));
  const pageServices = targetServices.slice(perPage * (page - 1), perPage * page);

  if (packageId === "") {
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

  const handleNavigatePackage = (serviceId) => {
    const preservedParams = preserveParams(location.search);
    preservedParams.set("serviceId", serviceId);
    navigate(`/packages/${packageId}?${preservedParams.toString()}`);
  };

  return (
    <Dialog open={show} onClose={handleClose} fullWidth maxWidth={isMdDown ? "xs" : "md"}>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography variant="h6">Selected Package</Typography>
          <KeyboardDoubleArrowRightIcon sx={{ ml: 0.5, mr: 0.5 }} />
          <Typography variant="h5" flexGrow={1}>
            {packageName}
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
              onClickService={handleNavigatePackage}
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
  packageId: PropTypes.string.isRequired,
  packageName: PropTypes.string.isRequired,
  serviceIds: PropTypes.arrayOf(PropTypes.string),
};
