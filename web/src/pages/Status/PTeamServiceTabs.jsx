import { UploadFile } from "@mui/icons-material";
import { Tabs, Tab, Tooltip, Box } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export function PTeamServiceTabs(props) {
  const { t } = useTranslation("status", { keyPrefix: "PTeamServiceTabs" });
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
              label={
                <Box
                  sx={(theme) => ({
                    display: "block",
                    width: "100%",
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                    textOverflow: "ellipsis",
                    paddingLeft: theme.spacing(1),
                    paddingRight: theme.spacing(1),
                  })}
                  component="span"
                >
                  {service.service_name}
                </Box>
              }
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
                minWidth: 0,
                padding: 0,
              }}
            />
          </Tooltip>
        ))}
        <Tab
          icon={<UploadFile />}
          label={t("upload")}
          aria-label="sbom file upload area button"
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
