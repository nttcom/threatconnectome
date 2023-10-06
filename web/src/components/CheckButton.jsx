import { Button, CircularProgress } from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

export default function CheckButton(props) {
  const { handleClick, isLoading } = props;

  return (
    <Button
      variant="outlined"
      sx={{
        textTransform: "none",
        marginRight: "10px",
      }}
      onClick={handleClick}
    >
      {isLoading ? <CircularProgress size="1.6rem" sx={{ color: "#fff" }} /> : "Check"}
    </Button>
  );
}

CheckButton.propTypes = {
  handleClick: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
};
