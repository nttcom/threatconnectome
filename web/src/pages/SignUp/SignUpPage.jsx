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
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import React, { useState } from "react";

import {
  useSendEmailVerificationMutation,
  useCreateUserWithEmailAndPasswordMutation,
} from "../../services/firebaseApi";

export function SignUp() {
  const [message, setMessage] = useState("");
  const [values, setValues] = useState({
    edited: new Set(),
    email: "",
    password: "",
    visible: false,
  });
  const [disabled, setDisabled] = useState(false);
  const [sendEmailVerification] = useSendEmailVerificationMutation();
  const [createUserWithEmailAndPassword] = useCreateUserWithEmailAndPasswordMutation();

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
      const userCredential = await createUserWithEmailAndPassword({
        email: values.email,
        password: values.password,
      }).unwrap();
      await sendEmailVerification({
        user: userCredential.user,
        actionCodeSettings: null,
      }).unwrap();
      setMessage("An email for verification was sent to your address.");
      setDisabled(true);
    } catch (error) {
      console.error(error);
      switch (error.code) {
        case "auth/internal-error":
          setMessage("Unauthorized Email Domain.");
          break;
        case "auth/email-already-in-use":
          setMessage("Email already in use.");
          break;
        case "auth/invalid-email":
          setMessage("Invalid email format.");
          break;
        case "auth/too-many-requests":
          setMessage("Too many requests.");
          break;
        case "auth/weak-password":
          setMessage("Weak password. Password should be at least 6 characters.");
          break;
        case "auth/operation-not-allowed":
        default:
          setMessage("Something went wrong.");
      }
    }
  };

  const handleVisibility = () => {
    setValues({ ...values, visible: !values.visible });
  };

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
            label="Email Address"
            margin="dense"
            onChange={handleChange("email")}
            required
            value={values.email}
            inputProps={{ pattern: "^.+@.+$" }}
          />
          <Tooltip arrow placement="bottom-end" title="Password should be at least 8 characters.">
            <TextField
              autoComplete="new-password"
              error={values.edited.has("password") && values.password.length < 8}
              fullWidth
              label="Password"
              margin="dense"
              onChange={handleChange("password")}
              required
              type={values.visible ? "text" : "password"}
              value={values.password}
              inputProps={{ minLength: 8 }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleVisibility}>
                      {values.visible ? <VisibilityIcon /> : <VisibilityOffIcon />}
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
            Sign up
          </Button>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="column" mt={3}>
          <Typography>{message}</Typography>
        </Box>
        <Typography align="center" variant="body1" style={{ color: "grey" }} mt={3}>
          This service is in closed beta. SIGNUP is only available for email addresses of authorized
          organizations.
        </Typography>
      </Container>
    </>
  );
}
