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

export function PTeamServiceSelectDialog(props) {
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
          justifyContent: "space-between",
          color: "black",
          borderColor: "rgba(0, 0, 0, 0.23)",
          minWidth: "180px",
          "&:hover": {
            borderColor: "rgba(0, 0, 0, 0.87)",
            backgroundColor: "rgba(0, 0, 0, 0.04)",
          },
        }}
        variant="outlined"
        endIcon={<ArrowDropDownIcon sx={{ color: "grey.700" }} />}
        onClick={handleClickOpen}
      >
        {services.find((s) => s.service_id === currentServiceId)?.service_name || "Select Service"}
      </Button>
      <Dialog fullWidth maxWidth="xs" open={open} onClose={handleClose}>
        <DialogTitle>Select a Service</DialogTitle>
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
                label={service.service_name}
              />
            ))}
          </RadioGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
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
