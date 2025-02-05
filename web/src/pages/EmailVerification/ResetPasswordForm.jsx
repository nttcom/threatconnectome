import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  IconButton,
  InputAdornment,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import {
  useVerifyPasswordResetCodeMutation,
  useConfirmPasswordResetMutation,
} from "../../services/firebaseApi";

export default function ResetPasswordForm(props) {
  const { oobCode } = props;
  const [disabled, setDisabled] = useState(false);
  const [message, setMessage] = useState(null);
  const [password, setPassword] = useState("");
  const [visible, setVisible] = useState(false);

  const [verifyPasswordResetCode] = useVerifyPasswordResetCodeMutation();
  const [confirmPasswordReset] = useConfirmPasswordResetMutation();

  async function handleResetPassword() {
    setDisabled(true);
    try {
      await verifyPasswordResetCode({ actionCode: oobCode }).unwrap();
      await confirmPasswordReset({ actionCode: oobCode, newPassword: password }).unwrap();
      setMessage("update password success");
    } catch (error) {
      console.error(error);
      setMessage("something went wrong");
    }
  }

  return (
    <Box alignItems="center" display="flex" flexDirection="column">
      <Typography variant="h5" my={2}>
        Reset Password
      </Typography>
      <Tooltip arrow placement="bottom-end" title="Password should be at least 8 characters.">
        <TextField
          autoComplete="new-password"
          error={password.length < 8}
          label="New Password"
          margin="normal"
          onChange={(event) => setPassword(event.target.value)}
          required
          type={visible ? "text" : "password"}
          value={password}
          inputProps={{ minLength: 8 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setVisible(!visible)}
                  aria-label="toggle password visibility"
                >
                  {visible ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </Tooltip>
      <Button
        onClick={() => handleResetPassword()}
        disabled={disabled || password.length < 8}
        variant="contained"
        sx={{ my: 2 }}
      >
        Submit
      </Button>
      <Box mt={3}>
        <Typography>{message}</Typography>
      </Box>
    </Box>
  );
}

ResetPasswordForm.propTypes = {
  oobCode: PropTypes.string.isRequired,
};
