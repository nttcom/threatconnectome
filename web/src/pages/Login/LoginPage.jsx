import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Container,
  CssBaseline,
  Divider,
  IconButton,
  InputAdornment,
  Link,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/auth";
import { useCreateUserMutation, useTryLoginMutation } from "../../services/tcApi";
import { setAuthUserIsReady } from "../../slices/auth";
import Firebase from "../../utils/Firebase";

import { TwoFactorAuth } from "./TwoFactorAuth";

export function Login() {
  const { t } = useTranslation("login", { keyPrefix: "LoginPage" });
  const [message, setMessage] = useState({ text: "", type: "" }); // type: 'info' | 'error'
  const [visible, setVisible] = useState(false);
  const [isShowSmsCode, setIsShowSmsCode] = useState(false);
  const [authData, setAuthData] = useState([]);
  const [isRecaptchaVisible, setIsRecaptchaVisible] = useState(false);
  const redirectedFrom = useSelector((state) => state.auth.redirectedFrom);

  const recaptchaId = "recaptcha-container-visible-login";

  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();

  const [createUser] = useCreateUserMutation();
  const [tryLogin] = useTryLoginMutation();
  const {
    sendEmailVerification,
    signInWithEmailAndPassword,
    signInWithSamlPopup,
    signInWithRedirect,
    signOut,
  } = useAuth();

  useEffect(() => {
    dispatch(setAuthUserIsReady(false));
    setMessage({ text: location.state?.message, type: location.state?.messageType });
    signOut();
  }, [dispatch, location, signOut]);

  useEffect(() => {
    const recaptcha_element = document.getElementById(recaptchaId);
    if (!recaptcha_element) return;

    const check = () => {
      setIsRecaptchaVisible(recaptcha_element.childElementCount > 0);
    };

    check();
    const observer = new MutationObserver(check);
    observer.observe(recaptcha_element, { childList: true });
    return () => observer.disconnect();
  }, []);

  const showMessage = (text, type = "error") => {
    setMessage({ text, type });
  };

  const callSignInWithEmailAndPassword = async (email, password) => {
    return await signInWithEmailAndPassword({
      email,
      password,
      recaptchaId: recaptchaId,
    }).catch((authError) => {
      showMessage(authError.message);
      return undefined;
    });
  };

  const navigateInternalPage = async () => {
    try {
      await tryLogin().unwrap();
      navigate({
        pathname: redirectedFrom.from ?? "/",
        search: redirectedFrom.search ?? "",
      });
    } catch (error) {
      switch (error.data?.detail) {
        case "Email is not verified. Try logging in on UI and verify email.": {
          const actionCodeSettings = { url: `${window.location.origin}/login` };
          await sendEmailVerification({ actionCodeSettings })
            .then(() => showMessage(t("emailNotVerified"), "info"))
            .catch((error) => showMessage(error.message));
          break;
        }
        case "No such user":
          createUser({ body: {} })
            .unwrap()
            .then(() =>
              navigate("/account", {
                state: {
                  from: redirectedFrom.from ?? "/",
                  search: redirectedFrom.search ?? "",
                },
              }),
            )
            .catch((error) => showMessage(error.data?.detail ?? t("somethingWentWrong")));
          break;
        default:
          showMessage(t("somethingWentWrong"));
          console.error(error);
      }
    }
  };

  const handleLoginWithEmail = async (event) => {
    event.preventDefault();
    showMessage(t("loggingIn"), "info");
    const data = new FormData(event.currentTarget);
    const authData = await callSignInWithEmailAndPassword(data.get("email"), data.get("password"));
    if (authData === undefined) return;
    if (import.meta.env.VITE_AUTH_SERVICE === "firebase" && authData?.mfa) {
      // Firebase SMS multi-factor auth
      setIsShowSmsCode(true);
      setAuthData(authData);
    } else {
      navigateInternalPage();
    }
  };

  const handleLoginWithSaml = () => {
    signInWithSamlPopup()
      .then(() => navigateInternalPage())
      .catch((error) => {
        showMessage(t("somethingWentWrong"));
        console.error(error);
      });
  };

  const handleLoginWithKeycloak = async () => {
    /* Note: currently, work with supabase only.
     * redirectTo: set the page which SUPABASE_AUTH_CONTAINER/auth/v1/callback should redirect to.
     */
    const redirectTo = `${window.location.origin}/auth_keycloak_callback`;
    await signInWithRedirect({ provider: "keycloak", redirectTo }).catch((authError) => {
      showMessage(authError.message);
      console.error(authError);
    });
  };

  const handleResetPassword = (event) => {
    event.preventDefault();
    navigate("/reset_password", {
      state: {
        from: redirectedFrom.from ?? "/",
        search: redirectedFrom.search ?? "",
      },
    });
  };
  const handleSignUp = (event) => {
    event.preventDefault();
    navigate("/sign_up", {
      state: {
        from: redirectedFrom.from ?? "/",
        search: redirectedFrom.search ?? "",
      },
    });
  };

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      {!isShowSmsCode && (
        <>
          <Box
            alignItems="center"
            component="form"
            display="flex"
            flexDirection="column"
            mt={1}
            onSubmit={handleLoginWithEmail}
          >
            <Typography component="h1" mb={1} variant="h5">
              {t("title")}
            </Typography>
            {!isRecaptchaVisible && (
              <>
                <TextField
                  autoComplete="email"
                  fullWidth
                  id="email"
                  label={t("emailLabel")}
                  margin="normal"
                  name="email"
                  required
                />
                <TextField
                  autoComplete="current-password"
                  fullWidth
                  id="password"
                  label={t("passwordLabel")}
                  margin="normal"
                  name="password"
                  required
                  type={visible ? "text" : "password"}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setVisible(!visible)}>
                          {visible ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <Link component="button" type="button" onClick={handleResetPassword}>
                  {t("forgotPassword")}
                </Link>
                <Button
                  fullWidth
                  type="submit"
                  variant="contained"
                  sx={{ textTransform: "none", mb: 2, mt: 3 }}
                >
                  {t("loginWithEmail")}
                </Button>
              </>
            )}
            <Box
              id={recaptchaId}
              sx={{
                mt: isRecaptchaVisible ? 5 : 0,
                mb: isRecaptchaVisible ? 5 : 0,
                width: "100%",
                display: "flex",
                justifyContent: "center",
              }}
            />
          </Box>
          {/* show saml login button if samlProviderId is set as env */}
          {!isRecaptchaVisible && Firebase.getSamlProvider() != null && (
            <>
              <Divider />
              <Button
                fullWidth
                onClick={handleLoginWithSaml}
                variant="contained"
                sx={{ textTransform: "none", mb: 2, mt: 2 }}
              >
                {t("loginWithSaml")}
              </Button>
            </>
          )}
          {/* show Keycloak login button if KEYCLOAK_ENABLED is true */}
          {/* currently, work with supabase only */}
          {import.meta.env.VITE_AUTH_SERVICE === "supabase" &&
            (import.meta.env.VITE_KEYCLOAK_ENABLED || "false").toLowerCase() === "true" && (
              <>
                <Divider />
                <Button
                  fullWidth
                  onClick={handleLoginWithKeycloak}
                  variant="contained"
                  sx={{ textTransform: "none", mb: 2, mt: 2 }}
                >
                  {t("loginWithKeycloak")}
                </Button>
              </>
            )}
          <Divider />
          <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" mt={1}>
            <Typography mr={1}>{t("noAccount")}</Typography>
            <Link component="button" onClick={handleSignUp} variant="body1">
              {t("signUp")}
            </Link>
          </Box>
          <Box alignItems="center" display="flex" flexDirection="column" mt={3}>
            <Typography color={message.type === "error" ? "error" : "textPrimary"}>
              {message.text}
            </Typography>
          </Box>
          <Typography align="center" variant="body1" style={{ color: "grey" }} mt={3}>
            {t("closedBetaNotice")}
          </Typography>
        </>
      )}
      {isShowSmsCode && (
        <TwoFactorAuth authData={authData} navigateInternalPage={navigateInternalPage} />
      )}
    </Container>
  );
}
