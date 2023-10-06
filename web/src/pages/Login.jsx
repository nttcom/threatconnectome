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
import { sendEmailVerification, signInWithEmailAndPassword } from "firebase/auth";
import React, { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { clearATeam } from "../slices/ateam";
import { clearGTeam } from "../slices/gteam";
import { clearPTeam } from "../slices/pteam";
import { clearUser } from "../slices/user";
import { createUser, getMyUserInfo, removeToken, setToken } from "../utils/api";
import { auth } from "../utils/firebase";

export const authCookieName = "Authorization";
export const cookiesOptions = { path: process.env.PUBLIC_URL || "/" };

export default function Login() {
  const [message, setMessage] = useState(null);
  const [visible, setVisible] = useState(false);

  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();

  /* eslint-disable-next-line no-unused-vars */
  const [_cookies, setCookie, removeCookie] = useCookies([authCookieName]);

  const metemcyberAuthUrl = process.env.REACT_APP_METEMCYBER_AUTH_URL;

  useEffect(() => {
    dispatch(clearUser());
    dispatch(clearPTeam());
    dispatch(clearATeam());
    dispatch(clearGTeam());
    removeCookie(authCookieName, cookiesOptions);
    removeToken();
    setMessage(location.state?.message);
  }, [dispatch, location, removeCookie]);

  const callSignInWithEmailAndPassword = async (email, password) => {
    try {
      return await signInWithEmailAndPassword(auth, email, password);
    } catch (error) {
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
      return;
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("Logging in...");
    const data = new FormData(event.currentTarget);
    const userCredential = await callSignInWithEmailAndPassword(
      data.get("email"),
      data.get("password")
    );
    if (userCredential === undefined) return;
    const { accessToken, email, uid } = userCredential.user;
    setToken(accessToken);
    setCookie(authCookieName, accessToken, cookiesOptions);
    try {
      await getMyUserInfo();
      navigate({
        pathname: location.state?.from ?? "/",
        search: location.state?.search ?? "",
      });
    } catch (error) {
      switch (error.response?.data?.detail) {
        case "Email is not verified. Try logging in on UI and verify email.": {
          let actionCodeSettings = {
            url: `${window.location.origin}${process.env.PUBLIC_URL}/login`,
          };
          await sendEmailVerification(userCredential.user, actionCodeSettings);
          setMessage(
            "Your email address is not verified. An email for verification was sent to your address."
          );
          break;
        }
        case "No such user":
          await createUser({ email, uid }); // other values are default
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

  const handleResetPassword = (event) => {
    event.preventDefault();
    navigate("/reset_password", {
      state: {
        from: location.state?.from ?? "/",
        search: location.state?.search ?? "",
      },
    });
  };

  const handleSignUp = () => {
    if (!metemcyberAuthUrl) return;
    window.open(metemcyberAuthUrl, "_blank");
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
        <Button fullWidth type="submit" variant="contained" sx={{ mb: 2, mt: 3 }}>
          Log In
        </Button>
      </Box>
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
