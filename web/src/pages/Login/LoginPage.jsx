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
import React, { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import {
  useSendEmailVerificationMutation,
  useSignInWithEmailAndPasswordMutation,
  useSignInWithSamlPopupMutation,
} from "../../services/firebaseApi";
import { useCreateUserMutation, useTryLoginMutation } from "../../services/tcApi";
import { clearAuth } from "../../slices/auth";
import Firebase from "../../utils/Firebase";
import { authCookieName, cookiesOptions } from "../../utils/const";

export function Login() {
  const [message, setMessage] = useState(null);
  const [visible, setVisible] = useState(false);

  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();

  const [_cookies, setCookie, removeCookie] = useCookies([authCookieName]);

  const [sendEmailVerification] = useSendEmailVerificationMutation();
  const [signInWithEmailAndPassword] = useSignInWithEmailAndPasswordMutation();
  const [signInWithSamlPopup] = useSignInWithSamlPopupMutation();
  const [createUser] = useCreateUserMutation();
  const [tryLogin] = useTryLoginMutation();

  useEffect(() => {
    dispatch(clearAuth());
    removeCookie(authCookieName, cookiesOptions);
    setMessage(location.state?.message);
  }, [dispatch, location, removeCookie]);

  const callSignInWithEmailAndPassword = async (email, password) => {
    return await signInWithEmailAndPassword({ email, password })
      .unwrap()
      .catch((error) => {
        switch (error.code) {
          case "auth/invalid-email":
            setMessage("Invalid email format.");
            break;
          case "auth/too-many-requests":
            setMessage("Too many requests.");
            break;
          case "auth/user-disabled":
            setMessage("Disabled user.");
            break;
          case "auth/user-not-found":
            setMessage("User not found.");
            break;
          case "auth/wrong-password":
            setMessage("Wrong password.");
            break;
          default:
            setMessage("Something went wrong.");
        }
        return undefined;
      });
  };

  const navigateInternalPage = async (userCredential) => {
    const accessToken = userCredential.user.accessToken;
    setCookie(authCookieName, accessToken, cookiesOptions);
    try {
      await tryLogin().unwrap();
      navigate({
        pathname: location.state?.from ?? "/",
        search: location.state?.search ?? "",
      });
    } catch (error) {
      switch (error.data?.detail) {
        case "Email is not verified. Try logging in on UI and verify email.": {
          const actionCodeSettings = {
            url: `${window.location.origin}${import.meta.env.VITE_PUBLIC_URL}/login`,
          };
          await sendEmailVerification({
            user: userCredential.user,
            actionCodeSettings: actionCodeSettings,
          });
          setMessage(
            "Your email address is not verified. An email for verification was sent to your address.",
          );
          break;
        }
        case "No such user":
          await createUser({}); // should get uid & email via firebase credential in api.
          // TODO: navigate to the first time login page, or say hello on snackbar.
          navigate("/account", {
            state: {
              from: location.state?.from ?? "/",
              search: location.state?.search ?? "",
            },
          });
          break;
        default:
          setMessage("Something went wrong.");
          console.error(error);
      }
    }
  };

  const handleLoginWithEmail = async (event) => {
    event.preventDefault();
    setMessage("Logging in...");
    const data = new FormData(event.currentTarget);
    const userCredential = await callSignInWithEmailAndPassword(
      data.get("email"),
      data.get("password"),
    );
    if (userCredential === undefined) return;
    navigateInternalPage(userCredential);
  };

  const handleLoginWithSaml = () => {
    signInWithSamlPopup()
      .unwrap()
      .then(async (userCredential) => {
        navigateInternalPage(userCredential);
      })
      .catch((error) => {
        setMessage("Something went wrong.");
        console.error(error);
      });
  };

  const handleResetPassword = (event) => {
    event.preventDefault();
    navigate("/reset_password", {
      state: {
        from: location.state?.from ?? "/",
        search: location.state?.search ?? "",
      },
    });
  };
  const handleSignUp = (event) => {
    event.preventDefault();
    navigate("/sign_up", {
      state: {
        from: location.state?.from ?? "/",
        search: location.state?.search ?? "",
      },
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
        onSubmit={handleLoginWithEmail}
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
        <TextField
          autoComplete="current-password"
          fullWidth
          id="password"
          label="Password"
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
          Forgot password?
        </Link>
        <Button
          fullWidth
          type="submit"
          variant="contained"
          sx={{ textTransform: "none", mb: 2, mt: 3 }}
        >
          Log In with Email
        </Button>
      </Box>
      {/* show saml login button if samlProviderId is set as env */}
      {Firebase.getSamlProvider() != null && (
        <>
          <Divider />
          <Button
            fullWidth
            onClick={handleLoginWithSaml}
            variant="contained"
            sx={{ textTransform: "none", mb: 2, mt: 2 }}
          >
            Log In with SAML
          </Button>
        </>
      )}
      <Divider />
      <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" mt={1}>
        <Typography mr={1}>No metemcyber account?</Typography>
        <Link component="button" onClick={handleSignUp} variant="body1">
          Sign up
        </Link>
      </Box>
      <Box alignItems="center" display="flex" flexDirection="column" mt={3}>
        <Typography>{message}</Typography>
      </Box>
      <Typography align="center" variant="body1" style={{ color: "grey" }} mt={3}>
        This service is in closed beta. LOGIN is only available for email addresses of authorized
        organizations.
      </Typography>
    </Container>
  );
}
