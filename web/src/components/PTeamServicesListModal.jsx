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
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate, useLocation } from "react-router-dom";

export function PTeamServicesListModal(props) {
  const { onSetShow, show, tagId, tagName, serviceIds } = props;
  const handleClose = () => onSetShow(false);

  const pteam = useSelector((state) => state.pteam.pteam);

  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);

  if (tagId === "") {
    return;
  }

  console.log("testes tagId:" + tagId);
  const targetServices = pteam.services
    .filter((service) => serviceIds.includes(service.service_id))
    .sort((a, b) => a.service_name.localeCompare(b.service_name));
  const pageServices = targetServices.slice(perPage * (page - 1), perPage * page);

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
    for (let key of ["tagId", "impactFilter", "word", "perPage", "page"]) {
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
            <Card
              key={service.service_id}
              onClick={() => handleNavigateTag(service.service_id)}
              variant="outlined"
              alignContent="space-between"
              sx={{ margin: 1, width: "100%", "&:hover": { bgcolor: grey[100] } }}
            >
              <CardHeader
                title={service.service_name}
                sx={{ backgroundColor: grey[200] }}
              ></CardHeader>
            </Card>
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
