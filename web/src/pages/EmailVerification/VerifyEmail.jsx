import { Box, Button, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useAuth } from "../../hooks/auth";

export default function VerifyEmail(props) {
  const { t } = useTranslation("emailVerification", { keyPrefix: "VerifyEmail" });
  const { oobCode } = props;
  const [disabled, setDisabled] = useState(false);
  const [message, setMessage] = useState(null);

  const { applyActionCode } = useAuth();

  function handleVerifyEmail() {
    setDisabled(true);
    applyActionCode({ actionCode: oobCode })
      .then((resp) => {
        setMessage(t("success"));
      })
      .catch((error) => {
        console.error(error);
        setMessage(error.message);
      });
  }

  return (
    <Box alignItems="center" display="flex" flexDirection="column">
      <Typography variant="h5" my={2}>
        {t("title")}
      </Typography>
      <Button
        onClick={() => handleVerifyEmail()}
        disabled={disabled}
        variant="contained"
        sx={{
          textTransform: "none",
        }}
      >
        {t("verifyButton")}
      </Button>
      <Box mt={3}>
        <Typography>{message}</Typography>
      </Box>
    </Box>
  );
}

VerifyEmail.propTypes = {
  oobCode: PropTypes.string,
};
