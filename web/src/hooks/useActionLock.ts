import { useEffect, useState } from "react";

export type UseActionLockReturn = {
  canExecute: boolean;
  timer: number;
  lockAction: () => void;
  unlockAction: () => void;
};

export function useActionLock(resendDelay = 5): UseActionLockReturn {
  const [canExecute, setCanExecute] = useState(true);
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    if (!canExecute) {
      const interval = setInterval(() => {
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

  const lockAction = (): void => {
    setCanExecute(false);
    setTimer(resendDelay);
  };

  const unlockAction = (): void => {
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
