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

// @ts-expect-error TS7016
import { PasswordField } from "../../components/PasswordField";
// @ts-expect-error TS7016
import { useAuth } from "../../hooks/auth";
import { getBearerToken } from "../../services/tcApi";

type MessageState = {
  text: string;
  type: "info" | "error" | "";
};

type SignUpFormState = {
  edited: Set<string>;
  email: string;
  password: string;
  confirmPassword: string;
  isVisible: boolean;
  isConfirmVisible: boolean;
};

type SignUpFormStringKey = "email" | "password" | "confirmPassword";
type SignUpFormBoolKey = "isVisible" | "isConfirmVisible";

export function SignUp() {
  const { t } = useTranslation("signUp", { keyPrefix: "SignUpPage" });
  const [message, setMessage] = useState({ text: "", type: "" });
  const [signUpForm, setSignUpForm] = useState<SignUpFormState>({
    edited: new Set<string>(),
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

  const showMessage = (text: string, type: MessageState["type"] = "error") => {
    setMessage({ text, type });
  };

  const handleFormChange =
    (prop: SignUpFormStringKey) => (event: React.ChangeEvent<HTMLInputElement>) => {
      signUpForm.edited.add(prop);
      setSignUpForm({
        ...signUpForm,
        [prop]: event.target.value,
      });
    };

  const handleForcedSignOut = async () => {
    try {
      const token = await getBearerToken();
      if (token) {
        await signOut();
      }
    } catch (tokenError) {
      console.error("Sign-out failed during cleanup:", tokenError);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (signUpForm.password !== signUpForm.confirmPassword) {
      showMessage(t("passwordsDoNotMatch"));
      return;
    }

    setDisabled(true);
    setIsLoading(true);

    try {
      await createUserWithEmailAndPassword({
        email: signUpForm.email.trim(),
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
      showMessage((error as Error).message);
      setDisabled(false);

      /**
       * If user creation succeeds but subsequent processes such as email sending encounter errors,
       * a forced sign-out is executed to prevent an incomplete login state from remaining on the client.
       */
      await handleForcedSignOut();
    } finally {
      setIsLoading(false);
    }
  };

  const handleVisibility = (prop: SignUpFormBoolKey) => {
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
            error={signUpForm.edited.has("email") && !signUpForm.email.trim().match(/^.+@.+$/)}
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
