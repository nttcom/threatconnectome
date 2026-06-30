import { Box, Button, Typography } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useAuth } from "../../hooks/auth";
import { authErrorToString } from "../../utils/authErrorUtils";

export type VerifyEmailProps = {
  oobCode: string | null;
};

export default function VerifyEmail({ oobCode }: VerifyEmailProps) {
  const { t } = useTranslation("emailVerification", { keyPrefix: "VerifyEmail" });
  const [disabled, setDisabled] = useState(false);
  const [message, setMessage] = useState<string | undefined>();

  const { applyActionCode } = useAuth();

  function handleVerifyEmail() {
    if (!oobCode) {
      return;
    }

    setDisabled(true);
    applyActionCode({ actionCode: oobCode })
      .then(() => {
        setMessage(t("success"));
      })
      .catch((error) => {
        console.error(error);
        setMessage(authErrorToString(error));
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
