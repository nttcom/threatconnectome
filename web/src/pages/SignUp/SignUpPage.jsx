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
  const [values, setValues] = useState({
    edited: new Set(),
    email: "",
    password: "",
    visible: false,
  });
  const [disabled, setDisabled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { createUserWithEmailAndPassword, sendEmailVerification } = useAuth();

  const handleChange = (prop) => (event) => {
    values.edited.add(prop);
    setValues({
      ...values,
      [prop]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await createUserWithEmailAndPassword({
        email: values.email,
        password: values.password,
      });
      if (
        import.meta.env.VITE_AUTH_SERVICE === "firebase" &&
        !import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_URL
        // TODO: should care about supabase + ENABLE_EMAIL_AUTO_CONFIRM=false?
      ) {
        await sendEmailVerification({ actionCodeSettings: null });
        setMessage(t("verificationEmailSent"));
      } else {
        setMessage(t("signUpSuccess"));
      }
      setDisabled(true);
    } catch (error) {
      console.error(error);
      setMessage(error.message);
    }
  };

  const handleVisibility = () => {
    setValues({ ...values, visible: !values.visible });
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
            error={values.edited.has("email") && !values.email.match(/^.+@.+$/)}
            fullWidth
            label={t("emailAddress")}
            margin="normal"
            onChange={handleChange("email")}
            required
            value={values.email}
            inputProps={{ pattern: "^.+@.+$" }}
          />

          <Tooltip arrow placement="bottom-end" title={t("passwordRequirement")}>
            <TextField
              autoComplete="new-password"
              error={values.edited.has("password") && values.password.length < 8}
              fullWidth
              label={t("password")}
              margin="normal"
              onChange={handleChange("password")}
              required
              type={values.visible ? "text" : "password"}
              value={values.password}
              inputProps={{ minLength: 8 }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleVisibility} aria-label="toggle password visibility">
                      {values.visible ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
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
          <Typography>{message}</Typography>
        </Box>
        <Typography align="center" variant="body1" style={{ color: "grey" }} mt={3}>
          {t("betaNotice")}
        </Typography>
      </Container>
    </>
  );
}
