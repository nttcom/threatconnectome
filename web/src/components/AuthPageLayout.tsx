import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";

import { LanguageSwitcher } from "../pages/App/LanguageSwitcher";

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
