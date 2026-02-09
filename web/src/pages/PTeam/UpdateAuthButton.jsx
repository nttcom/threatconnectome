import { Button } from "@mui/material";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import dialogStyle from "../../cssModule/dialog.module.css";

export function UpdateAuthButton(props) {
  const { disabled, onUpdate } = props;
  const { t } = useTranslation("pteam", { keyPrefix: "UpdateAuthButton" });

  return (
    <Button disabled={disabled} onClick={onUpdate} className={dialogStyle.submit_btn}>
      {t("update")}
    </Button>
  );
}

UpdateAuthButton.propTypes = {
  disabled: PropTypes.bool.isRequired,
  onUpdate: PropTypes.func.isRequired,
};
