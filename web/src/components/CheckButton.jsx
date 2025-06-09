import { Button, CircularProgress } from "@mui/material";
import PropTypes from "prop-types";

import styles from "../cssModule/button.module.css";

export function CheckButton(props) {
  const { onHandleClick, isLoading } = props;

  return (
    <Button className={styles.check_btn} onClick={onHandleClick}>
      {isLoading ? <CircularProgress size="1.6rem" sx={{ color: "#fff" }} /> : "Check"}
    </Button>
  );
}

CheckButton.propTypes = {
  onHandleClick: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
};
