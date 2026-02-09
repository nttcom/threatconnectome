import { Button, CircularProgress } from "@mui/material";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import styles from "../cssModule/button.module.css";

export function CheckButton(props) {
  const { onHandleClick, isLoading } = props;
  const { t } = useTranslation("components", { keyPrefix: "CheckButton" });

  return (
    <Button className={styles.check_btn} onClick={onHandleClick}>
      {isLoading ? <CircularProgress size="1.6rem" sx={{ color: "#fff" }} /> : t("check")}
    </Button>
  );
}

CheckButton.propTypes = {
  onHandleClick: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
};
