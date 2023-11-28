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
import { multiFactor, TotpMultiFactorGenerator } from "firebase/auth";
import { useQRCode } from "next-qrcode";
import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { auth } from "../utils/firebase";

export default function SetupTotp() {
  const [disabled, setDisabled] = useState(false);
  const [message, setMessage] = useState(null);
  const [qrcodeUrl, setQrcodeUrl] = useState(null);
  const [verificationCode, setVerificationCode] = useState("");

  const location = useLocation();
  const navigate = useNavigate();
  const { Canvas } = useQRCode();

  const handleLogIn = () =>
    navigate("/login", {
      state: {
        from: location.state?.from ?? "/",
        search: location.state?.search ?? "",
      },
    });

  const handleGenerateQR = async (event) => {
    event.preventDefault();
    // setDisabled(true);
    setMessage("Processing...");

    if (auth.currentUser === null) return;

    const multiFactorSession = await multiFactor(auth.currentUser).getSession();
    const totpSecret = await TotpMultiFactorGenerator.generateSecret(multiFactorSession);

    // Display this URL as a QR code.
    const appName = "metemcyber";

    try {
      const url = totpSecret.generateQrCodeUrl(auth.currentUser.uid, appName);
      setQrcodeUrl(url);
    } catch (error) {
      setDisabled(false);
      console.log(error);
    }
    setMessage("create QR code");
  };

  const handleSetupTotp = async (event) => {
    const multiFactorSession = await multiFactor(auth.currentUser).getSession();

    const totpSecret = await TotpMultiFactorGenerator.generateSecret(multiFactorSession);

    // const verificationCode = "";
    console.log(verificationCode);
    const multiFactorAssertion = TotpMultiFactorGenerator.assertionForEnrollment(
      totpSecret,
      verificationCode
    );

    try {
      // Finalize the enrollment.
      multiFactor(auth.currentUser).enroll(multiFactorAssertion, "totp");
    } catch (error) {
      setDisabled(false);
      console.log(error);

      return;
    }
    setMessage("setup success");
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
        onSubmit={handleGenerateQR}
      >
        <Typography component="h1" mb={1} variant="h5">
          Threatconnectome
        </Typography>

        <Button
          color="warning"
          disabled={disabled}
          fullWidth
          type="submit"
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
        >
          generate QR code
        </Button>
      </Box>
      {qrcodeUrl && (
        <Canvas
          text={qrcodeUrl}
          options={{
            errorCorrectionLevel: "M",
            margin: 3,
            scale: 4,
            width: 200,
          }}
        />
      )}
      <TextField
        value={verificationCode}
        onChange={(event) => setVerificationCode(event.target.value)}
        fullWidth
        label="code"
        margin="normal"
        name="code"
      />
      <Button
        color="warning"
        onClick={handleSetupTotp}
        disabled={disabled}
        fullWidth
        type="submit"
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
      >
        Setup TOTP
      </Button>
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
