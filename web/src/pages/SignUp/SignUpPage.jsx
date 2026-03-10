import {
  Box,
  Button,
  Container,
  CssBaseline,
  TextField,
  Link,
  Typography,
  CircularProgress,
} from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { PasswordField } from "../../components/PasswordField";
import { useAuth } from "../../hooks/auth";
import { getBearerToken } from "../../services/tcApi";

export function SignUp() {
  const { t } = useTranslation("signUp", { keyPrefix: "SignUpPage" });
  const [message, setMessage] = useState({ text: "", type: "" }); // type: 'info' | 'error'
  const [signUpForm, setSignUpForm] = useState({
    edited: new Set(),
    email: "",
    password: "",
    confirmPassword: "",
    isVisible: false,
    isConfirmVisible: false,
  });
  const [disabled, setDisabled] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { createUserWithEmailAndPassword, sendEmailVerification, signOut } = useAuth();

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

    setDisabled(true);
    setIsLoading(true);

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

      /**
       * After completing the new registration, do not remain logged in; sign out once.
       * This prevents unexpected screen transitions triggered by onAuthStateChanged in LoginPage.jsx.
       * Sign out to maintain consistency with the TC database.
       */
      await signOut();
    } catch (error) {
      console.error(error);
      showMessage(error.message);
      setDisabled(false);

      /**
       * If user creation succeeds but subsequent processes such as email sending encounter errors,
       * a forced sign-out is executed to prevent an incomplete login state from remaining on the client.
       */
      const token = await getBearerToken();
      if (token) {
        await signOut();
      }
    } finally {
      setIsLoading(false);
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

          <PasswordField
            name="password"
            label={t("password")}
            value={signUpForm.password}
            edited={signUpForm.edited}
            onChange={handleFormChange("password")}
            isVisible={signUpForm.isVisible}
            onToggle={() => handleVisibility("isVisible")}
            tooltipTitle={t("passwordRequirement")}
          />

          <PasswordField
            name="confirmPassword"
            label={t("confirmPassword")}
            value={signUpForm.confirmPassword}
            edited={signUpForm.edited}
            onChange={handleFormChange("confirmPassword")}
            isVisible={signUpForm.isConfirmVisible}
            onToggle={() => handleVisibility("isConfirmVisible")}
            tooltipTitle={t("passwordRequirement")}
          />
          <Button
            disabled={
              disabled || signUpForm.password.length < 8 || signUpForm.confirmPassword.length < 8
            }
            startIcon={isLoading ? <CircularProgress size={20} /> : null}
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
