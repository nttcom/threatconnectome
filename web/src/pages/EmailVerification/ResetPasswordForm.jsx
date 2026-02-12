import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  IconButton,
  InputAdornment,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useAuth } from "../../hooks/auth";

export default function ResetPasswordForm(props) {
  const { t } = useTranslation("emailVerification", { keyPrefix: "ResetPasswordForm" });
  const { oobCode } = props;
  const [disabled, setDisabled] = useState(false);
  const [message, setMessage] = useState(null);
  const [password, setPassword] = useState("");
  const [visible, setVisible] = useState(false);

  const { verifyPasswordResetCode, confirmPasswordReset } = useAuth();

  async function handleResetPassword() {
    setDisabled(true);
    await verifyPasswordResetCode({ actionCode: oobCode })
      .then(() => confirmPasswordReset({ actionCode: oobCode, newPassword: password }))
      .then(() => setMessage(t("success")))
      .catch((error) => {
        console.error(error);
        setMessage(error.message);
      });
  }

  if (import.meta.env.VITE_AUTH_SERVICE === "supabase") {
    return <>{t("notSupported")}</>;
  }
  if (!oobCode) {
    return <>{t("missingCode")}</>;
  }

  return (
    <Box alignItems="center" display="flex" flexDirection="column">
      <Typography variant="h5" my={2}>
        {t("title")}
      </Typography>
      <Tooltip arrow placement="bottom-end" title={t("passwordHint")}>
        <TextField
          autoComplete="new-password"
          error={password.length < 8}
          label={t("newPassword")}
          margin="normal"
          onChange={(event) => setPassword(event.target.value)}
          required
          type={visible ? "text" : "password"}
          value={password}
          inputProps={{ minLength: 8 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setVisible(!visible)}
                  aria-label="toggle password visibility"
                >
                  {visible ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </Tooltip>
      <Button
        onClick={() => handleResetPassword()}
        disabled={disabled || password.length < 8}
        variant="contained"
        sx={{ my: 2 }}
      >
        {t("submit")}
      </Button>
      <Box mt={3}>
        <Typography>{message}</Typography>
      </Box>
    </Box>
  );
}

ResetPasswordForm.propTypes = {
  oobCode: PropTypes.string,
};
