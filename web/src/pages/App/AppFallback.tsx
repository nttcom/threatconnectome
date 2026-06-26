import { Box, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";
import type { FallbackProps } from "react-error-boundary";

import { APIError } from "../../utils/APIError";

export function AppFallback({ error }: FallbackProps) {
  const { t } = useTranslation("app", { keyPrefix: "AppFallback" });
  console.log(error);
  return (
    <Box>
      <Typography>{t("somethingWentWrong")}</Typography>
      {error instanceof APIError && (
        <Typography>
          {t("calledAPI")} {error.api || "unknown"}
        </Typography>
      )}
    </Box>
  );
}
