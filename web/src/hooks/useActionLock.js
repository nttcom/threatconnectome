import { useEffect, useState } from "react";

export function useActionLock(resendDelay = 5) {
  const [canExecute, setCanExecute] = useState(true);
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    if (!canExecute) {
      let interval = setInterval(() => {
        setTimer((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            setCanExecute(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [canExecute]);

  const lockAction = () => {
    setCanExecute(false);
    setTimer(resendDelay);
  };

  const unlockAction = () => {
    setCanExecute(true);
    setTimer(0);
  };

  return {
    canExecute,
    timer,
    lockAction,
    unlockAction,
  };
}
