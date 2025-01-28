import React from "react";
import { useLocation } from "react-router-dom";

import ResetPassword from "./ResetPassword";
import VerifyEmail from "./VerifyEmail";

export function EmailVerification() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);

  const mode = params.get("mode");
  const oobCode = params.get("oobCode");

  switch (mode) {
    case "verifyEmail":
      return <VerifyEmail oobCode={oobCode} />;
    case "resetPassword":
      return <ResetPassword oobCode={oobCode} />;
    case "recoverEmail":
      // future work?
      break;
    default:
      console.error("Invalid mode");
  }
}
