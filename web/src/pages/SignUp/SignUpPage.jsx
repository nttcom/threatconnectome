import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Container,
  CssBaseline,
  IconButton,
  InputAdornment,
  Link,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/auth";

export function SignUp() {
  const { t } = useTranslation("signUp", { keyPrefix: "SignUpPage" });
  const [message, setMessage] = useState("");
  const [signUpForm, setSignUpForm] = useState({
    edited: new Set(),
    email: "",
    password: "",
    confirmPassword: "",
    isVisible: false,
    isConfirmVisible: false,
  });
  const [disabled, setDisabled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { createUserWithEmailAndPassword, sendEmailVerification } = useAuth();

  const showMessage = (text, type = "error") => {
    setMessage({ text, type });
  };

  const handleFormChange = (prop) => (event) => {
    signUpForm.edited.add(prop);
    setSignUpForm({
      ...signUpForm,
      [prop]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (signUpForm.password !== signUpForm.confirmPassword) {
      showMessage(t("passwordsDoNotMatch"));
      return;
    }

    try {
      await createUserWithEmailAndPassword({
        email: signUpForm.email,
        password: signUpForm.password,
      });
      if (
        import.meta.env.VITE_AUTH_SERVICE === "firebase" &&
        !import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_URL
        // TODO: should care about supabase + ENABLE_EMAIL_AUTO_CONFIRM=false?
      ) {
        await sendEmailVerification({ actionCodeSettings: null });
        showMessage(t("verificationEmailSent"), "info");
      } else {
        showMessage(t("signUpSuccess"), "info");
      }
      setDisabled(true);
    } catch (error) {
      console.error(error);
      showMessage(error.message);
    }
  };

  const handleVisibility = (prop) => {
    setSignUpForm((prev) => ({ ...prev, [prop]: !prev[prop] }));
  };

  const handleLogIn = () =>
    navigate("/login", {
      state: {
        from: location.state?.from ?? "/",
        search: location.state?.search ?? "",
      },
    });

  return (
    <>
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
            error={signUpForm.edited.has("email") && !signUpForm.email.match(/^.+@.+$/)}
            fullWidth
            label={t("emailAddress")}
            margin="normal"
            onChange={handleFormChange("email")}
            required
            value={signUpForm.email}
            slotProps={{ htmlInput: { pattern: "^.+@.+$" } }}
          />

          <Tooltip arrow placement="bottom-end" title={t("passwordRequirement")}>
            <TextField
              autoComplete="new-password"
              error={signUpForm.edited.has("password") && signUpForm.password.length < 8}
              fullWidth
              label={t("password")}
              margin="normal"
              onChange={handleFormChange("password")}
              required
              type={signUpForm.isVisible ? "text" : "password"}
              value={signUpForm.password}
              slotProps={{
                htmlInput: { minLength: 8 },
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => handleVisibility("isVisible")}
                        aria-label="toggle password visibility"
                      >
                        {signUpForm.isVisible ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
            />
          </Tooltip>
          <Tooltip arrow placement="bottom-end" title={t("passwordRequirement")}>
            <TextField
              autoComplete="new-password"
              error={
                signUpForm.edited.has("confirmPassword") && signUpForm.confirmPassword.length < 8
              }
              fullWidth
              label={t("confirmPassword")}
              margin="normal"
              onChange={handleFormChange("confirmPassword")}
              required
              type={signUpForm.isConfirmVisible ? "text" : "password"}
              value={signUpForm.confirmPassword}
              slotProps={{
                htmlInput: { minLength: 8 },
                input: {
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => handleVisibility("isConfirmVisible")}
                        aria-label="toggle confirm password visibility"
                      >
                        {signUpForm.isConfirmVisible ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
            />
          </Tooltip>
          <Button
            disabled={disabled}
            color="success"
            fullWidth
            type="submit"
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            {t("signUp")}
          </Button>
        </Box>
        <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" mt={1}>
          <Link component="button" onClick={handleLogIn} variant="body1">
            {t("backToLogIn")}
          </Link>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="column" mt={3}>
          <Typography color={message.type === "error" ? "error" : "textPrimary"}>
            {message.text}
          </Typography>
        </Box>
        <Typography align="center" variant="body1" style={{ color: "grey" }} mt={3}>
          {t("betaNotice")}
        </Typography>
      </Container>
    </>
  );
}
