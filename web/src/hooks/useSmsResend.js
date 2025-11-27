import { useEffect, useState } from "react";

export function useSmsResend(resendDelay = 5) {
  const [canResend, setCanResend] = useState(true);
  const [timer, setTimer] = useState(0);
  const [notification, setNotification] = useState({ open: false, message: "", type: "info" });

  useEffect(() => {
    if (!canResend) {
      let interval = setInterval(() => {
        setTimer((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            setCanResend(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [canResend]);

  const startResendTimer = () => {
    setCanResend(false);
    setTimer(resendDelay);
  };

  const resetResendState = () => {
    setCanResend(true);
    setTimer(0);
  };

  const showNotification = (message, type = "info") => {
    setNotification({ open: true, message, type });
  };

  const closeNotification = () => {
    setNotification({ ...notification, open: false });
  };

  return {
    canResend,
    timer,
    notification,
    startResendTimer,
    resetResendState,
    showNotification,
    closeNotification,
  };
}
