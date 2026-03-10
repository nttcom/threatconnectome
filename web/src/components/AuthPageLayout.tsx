import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";

import { LanguageSwitcher } from "./LanguageSwitcher";

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
        <LanguageSwitcher collapseOnMobile={false} />
      </Box>
      <Outlet />
    </>
  );
}
