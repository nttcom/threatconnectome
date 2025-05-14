import {
  Box,
  Button,
  Container,
  CssBaseline,
  Divider,
  Link,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/auth";

export function ResetPassword() {
  const [disabled, setDisabled] = useState(false);
  const [message, setMessage] = useState(null);

  const location = useLocation();
  const navigate = useNavigate();
  const { sendPasswordResetEmail } = useAuth();

  const handleBackToLogIn = () => navigate("/login");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setDisabled(true);
    setMessage("Processing...");
    const data = new FormData(event.currentTarget);
    // actionCodeSettings for Firebase
    const actionCodeSettings = {
      handleCodeInApp: false,
      url: `${window.location.origin}${import.meta.env.VITE_PUBLIC_URL}/login`,
    };
    // redirectTo for Supabase
    const redirectTo =
      `${window.location.origin}${import.meta.env.VITE_PUBLIC_URL}` +
      "/email_verification?mode=resetPassword";
    await sendPasswordResetEmail({
      email: data.get("email"),
      actionCodeSettings,
      redirectTo,
    })
      .then(() => {
        let msg = "An email with a password reset URL was sent to this address.";
        if (
          import.meta.env.VITE_AUTH_SERVICE !== "firebase" ||
          import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_URL
        ) {
          msg += " (Maybe no email is actually sent by current auth provider)";
        }
        setMessage(msg);
      })
      .catch((error) => {
        setDisabled(false);
        setMessage(error.message);
      });
  };

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <Box
        alignItems="center"
        component="form"
        display="flex"
        flexDirection="column"
        mt={1}
        onSubmit={handleSubmit}
      >
        <Typography component="h1" mb={1} variant="h5">
          Threatconnectome
        </Typography>
        <TextField
          autoComplete="email"
          fullWidth
          id="email"
          label="Email Address"
          margin="normal"
          name="email"
          required
        />
        <Button
          color="warning"
          disabled={disabled}
          fullWidth
          type="submit"
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
        >
          Reset Password
        </Button>
      </Box>
      <Divider />
      <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" mt={1}>
        <Link component="button" onClick={handleBackToLogIn} variant="body1">
          Back to log in
        </Link>
      </Box>
      <Box alignItems="center" display="flex" flexDirection="column" mt={3}>
        <Typography>{message}</Typography>
      </Box>
    </Container>
  );
}
