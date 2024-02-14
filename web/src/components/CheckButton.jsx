import { Button, CircularProgress } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

export function CheckButton(props) {
  const { onHandleClick, isLoading } = props;

  return (
    <Button
      variant="outlined"
      sx={{
        textTransform: "none",
        marginRight: "10px",
      }}
      onClick={onHandleClick}
    >
      {isLoading ? <CircularProgress size="1.6rem" sx={{ color: "#fff" }} /> : "Check"}
    </Button>
  );
}

CheckButton.propTypes = {
  onHandleClick: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
};
