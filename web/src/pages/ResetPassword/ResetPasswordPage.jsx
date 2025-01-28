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
import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useSendPasswordResetEmailMutation } from "../../services/firebaseApi";

export function ResetPassword() {
  const [disabled, setDisabled] = useState(false);
  const [message, setMessage] = useState(null);

  const [sendPasswordResetEmail] = useSendPasswordResetEmailMutation();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogIn = () =>
    navigate("/login", {
      state: {
        from: location.state?.from ?? "/",
        search: location.state?.search ?? "",
      },
    });

  const handleSubmit = async (event) => {
    event.preventDefault();
    setDisabled(true);
    setMessage("Processing...");
    const data = new FormData(event.currentTarget);
    const actionCodeSettings = {
      handleCodeInApp: false,
      url: `${window.location.origin}${import.meta.env.VITE_PUBLIC_URL}/login`,
    };
    try {
      await sendPasswordResetEmail({
        email: data.get("email"),
        actionCodeSettings: actionCodeSettings,
      }).unwrap();
      setMessage("An email with a password reset URL was sent to this address.");
    } catch (error) {
      setDisabled(false);
      switch (error.code) {
        case "auth/invalid-email":
          setMessage("Invalid email format.");
          break;
        case "auth/user-not-found":
          setMessage("User does not exist. Check the email address.");
          break;
        default:
          setMessage("Something went wrong.");
      }
    }
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
        <Link component="button" onClick={handleLogIn} variant="body1">
          Back to log in
        </Link>
      </Box>
      <Box alignItems="center" display="flex" flexDirection="column" mt={3}>
        <Typography>{message}</Typography>
      </Box>
    </Container>
  );
}
