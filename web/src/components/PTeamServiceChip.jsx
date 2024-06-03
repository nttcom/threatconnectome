import { Box, Chip } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import { getPTeamServices } from "../slices/pteam";

export function PTeamServiceChip() {
  const dispatch = useDispatch();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const services = useSelector((state) => state.pteam.services);

  useEffect(() => {
    if (!pteamId) return;
    if (!services) {
      dispatch(getPTeamServices(pteamId));
    }
  }, [pteamId, services, dispatch]);

  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const selectedService = params.get("service") ?? "";

  const handleSelectService = (service) => {
    if (service === selectedService) {
      params.delete("service");
    } else {
      params.set("service", service);
      params.set("page", 1); // reset page
    }
    navigate(location.pathname + "?" + params.toString());
  };

  return (
    <>
      <Box>
        {services &&
          services.map((service) => (
            <Chip
              key={service}
              label={service}
              variant={service === selectedService ? "" : "outlined"}
              sx={{
                mt: 1,
                borderRadius: "2px",
                border: `1px solid ${grey[300]}`,
                borderLeft: `5px solid ${grey[300]}`,
                mr: 1,
                background: service === selectedService ? grey[400] : "",
              }}
              onClick={() => {
                handleSelectService(service);
              }}
            />
          ))}
      </Box>
    </>
  );
}
