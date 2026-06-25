import { Refresh } from "@mui/icons-material";
import { Button, Stack } from "@mui/material";
import { useTranslation } from "react-i18next";

type SmsResendButtonProps = {
  canExecute: boolean;
  isBusy?: boolean;
  timer: number;
  onResend: () => void;
};

export function SmsResendButton({
  canExecute,
  isBusy = false,
  timer,
  onResend,
}: SmsResendButtonProps) {
  const { t } = useTranslation("components", { keyPrefix: "SmsResendButton" });
  const disabled = !canExecute || isBusy;

  return (
    <Button size="small" disabled={disabled} onClick={onResend} sx={{ fontWeight: "bold" }}>
      {canExecute ? (
        <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
          <Refresh fontSize="small" />
          <span>{t("resend")}</span>
        </Stack>
      ) : (
        t("resendIn", { timer })
      )}
    </Button>
  );
}
