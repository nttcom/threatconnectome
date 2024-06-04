import { Tabs, Tab } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import { getPTeamServices } from "../slices/pteam";

export function PTeamServiceChip() {
  const dispatch = useDispatch();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const services = useSelector((state) => state.pteam.services);

  const [value, setValue] = React.useState(0);

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

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

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
      <Tabs
        value={value}
        onChange={handleChange}
        variant="scrollable"
        scrollButtons="auto"
        aria-label="scrollable auto tabs example"
      >
        {services &&
          services.map((service) => (
            <Tab
              key={service}
              label={service}
              onClick={() => {
                handleSelectService(service);
              }}
              sx={{
                textTransform: "none",
                border: `1px solid ${grey[300]}`,
                borderRadius: "0.5rem 0.5rem 0 0",
              }}
            />
          ))}
      </Tabs>
    </>
  );
}
