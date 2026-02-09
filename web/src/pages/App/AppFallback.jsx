import { Box, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { APIError } from "../../utils/APIError";

export function AppFallback({ error }) {
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
AppFallback.propTypes = {
  error: PropTypes.object.isRequired,
};
