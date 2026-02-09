import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Radio,
  RadioGroup,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export function PTeamServiceSelectDialog(props) {
  const { t } = useTranslation("status", { keyPrefix: "PTeamServiceSelectDialog" });
  const { services, currentServiceId, onChangeService, setIsActiveUploadMode } = props;
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(currentServiceId);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <Box>
      <Button
        sx={{
          textTransform: "none",
          color: "black",
          borderColor: "rgba(0, 0, 0, 0.23)",
          minWidth: "180px",
          maxWidth: "220px",
          "&:hover": {
            borderColor: "rgba(0, 0, 0, 0.87)",
            backgroundColor: "rgba(0, 0, 0, 0.04)",
          },
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          paddingRight: "12px",
        }}
        variant="outlined"
        onClick={handleClickOpen}
      >
        <Box
          sx={{
            flex: 1,
            overflow: "hidden",
            whiteSpace: "nowrap",
            textOverflow: "ellipsis",
            textAlign: "left",
          }}
        >
          {services.find((s) => s.service_id === currentServiceId)?.service_name ||
            t("selectService")}
        </Box>
        <ArrowDropDownIcon sx={{ color: "grey.700", marginLeft: "8px", flexShrink: 0 }} />
      </Button>
      <Dialog fullWidth maxWidth="xs" open={open} onClose={handleClose}>
        <DialogTitle>{t("selectAService")}</DialogTitle>
        <DialogContent dividers>
          <RadioGroup
            value={selected}
            onChange={(event) => {
              const value = event.target.value;
              setSelected(value);
              if (value !== currentServiceId) {
                onChangeService(value);
                if (setIsActiveUploadMode) setIsActiveUploadMode(0);
              }
              setOpen(false);
            }}
          >
            {services.map((service) => (
              <FormControlLabel
                key={service.service_id}
                value={service.service_id}
                control={<Radio />}
                label={
                  <Box
                    sx={{
                      maxWidth: "100%",
                      overflow: "hidden",
                      wordBreak: "break-all",
                      whiteSpace: "normal",
                      display: "block",
                    }}
                  >
                    {service.service_name}
                  </Box>
                }
              />
            ))}
          </RadioGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>{t("cancel")}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

PTeamServiceSelectDialog.propTypes = {
  services: PropTypes.array.isRequired,
  currentServiceId: PropTypes.string.isRequired,
  onChangeService: PropTypes.func.isRequired,
  setIsActiveUploadMode: PropTypes.func.isRequired,
};
