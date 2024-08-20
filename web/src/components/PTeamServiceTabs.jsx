import { UploadFile } from "@mui/icons-material";
import { Tabs, Tab, Tooltip } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";

export function PTeamServiceTabs(props) {
  const { services, currentServiceId, onChangeService, setIsActiveUploadMode } = props;

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
          <Tooltip key={service.service_id} title={service.service_name}>
            <Tab
              label={service.service_name}
              onClick={() => {
                onChangeService(service.service_id);
                setIsActiveUploadMode(0);
              }}
              sx={{
                textTransform: "none",
                border: `1px solid ${grey[300]}`,
                borderRadius: "0.5rem 0.5rem 0 0",
                width: "20%",
                mt: 1,
              }}
            />
          </Tooltip>
        ))}
        <Tab
          icon={<UploadFile />}
          label="Upload"
          onClick={() => setIsActiveUploadMode(1)}
          sx={{
            textTransform: "none",
            border: `1px solid ${grey[300]}`,
            borderRadius: "0.5rem 0.5rem 0 0",
            width: "20%",
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
  setIsActiveUploadMode: PropTypes.func.isRequired,
};
