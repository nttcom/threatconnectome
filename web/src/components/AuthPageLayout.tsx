import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";

import { LanguageSwitcher } from "../pages/App/LanguageSwitcher";

/**
 * Layout route for authentication pages (Login, SignUp, ResetPassword, EmailVerification).
 * Places a LanguageSwitcher in the top-right corner of the page.
 */
export function AuthPageLayout() {
  return (
    <>
      <Box
        sx={{
          display: "flex",
          justifyContent: "flex-end",
          px: 2,
          pt: 2,
        }}
      >
        <LanguageSwitcher compact={false} />
      </Box>
      <Outlet />
    </>
  );
}
