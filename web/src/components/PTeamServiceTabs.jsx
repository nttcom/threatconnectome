import { UploadFile } from "@mui/icons-material";
import { Tabs, Tab } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";

export function PTeamServiceTabs(props) {
  const { services, currentServiceId, onChangeService, setIsUploadMode } = props;

  const serviceIds = services.map((service) => service.service_id);
  const currentIndex = serviceIds.findIndex((serviceId) => serviceId === currentServiceId);
  const [value, setValue] = useState(currentIndex);

  return (
    <>
      <Tabs
        value={value}
        onChange={(event, newValue) => setValue(newValue)}
        variant="scrollable"
        scrollButtons="auto"
        aria-label="scrollable auto tabs example"
      >
        {services.map((service) => (
          <Tab
            key={service.service_id}
            label={service.service_name}
            onClick={() => {
              onChangeService(service.service_id);
              setIsUploadMode(0);
            }}
            sx={{
              textTransform: "none",
              border: `1px solid ${grey[300]}`,
              borderRadius: "0.5rem 0.5rem 0 0",
              width: "10%",
              mt: 1,
            }}
          />
        ))}
        <Tab
          icon={<UploadFile />}
          label="Upload"
          onClick={() => setIsUploadMode(1)}
          sx={{
            textTransform: "none",
            border: `1px solid ${grey[300]}`,
            borderRadius: "0.5rem 0.5rem 0 0",
            width: "10%",
            mt: 1,
          }}
        />
      </Tabs>
    </>
  );
}

PTeamServiceTabs.propTypes = {
  services: PropTypes.array.isRequired,
  currentServiceId: PropTypes.string.isRequired,
  onChangeService: PropTypes.func.isRequired,
  setIsUploadMode: PropTypes.func.isRequired,
};
