import { Refresh } from "@mui/icons-material";
import { Button, Stack } from "@mui/material";
import PropTypes from "prop-types";

export function SmsResendButton({ canExecute, isBusy, timer, onResend }) {
  const disabled = !canExecute || isBusy;

  return (
    <Button size="small" disabled={disabled} onClick={onResend} sx={{ fontWeight: "bold" }}>
      {canExecute ? (
        <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
          <Refresh fontSize="small" />
          <span>Resend the code</span>
        </Stack>
      ) : (
        `Resend in ${timer} seconds`
      )}
    </Button>
  );
}

SmsResendButton.propTypes = {
  canExecute: PropTypes.bool.isRequired,
  isBusy: PropTypes.bool,
  timer: PropTypes.number.isRequired,
  onResend: PropTypes.func.isRequired,
};

SmsResendButton.defaultProps = {
  isBusy: false,
};
