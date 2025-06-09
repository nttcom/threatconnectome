import { Button } from "@mui/material";
import PropTypes from "prop-types";

import dialogStyle from "../../cssModule/dialog.module.css";

export function UpdateAuthButton(props) {
  const { disabled, onUpdate } = props;

  return (
    <Button disabled={disabled} onClick={onUpdate} className={dialogStyle.submit_btn}>
      Update
    </Button>
  );
}

UpdateAuthButton.propTypes = {
  disabled: PropTypes.bool.isRequired,
  onUpdate: PropTypes.func.isRequired,
};
