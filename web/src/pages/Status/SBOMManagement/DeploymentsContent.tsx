import LocationOnIcon from "@mui/icons-material/LocationOn";
import { Box, CardContent, Stack, TextField, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { maxAssetAddressLengthInHalf } from "../../../utils/const";
import { getLengthError } from "../../../utils/SBOMManagement/formValidation";
import { normalizeCommaSeparatedValues } from "../../../utils/SBOMManagement/sbomManagementUtils";

import { fieldSx, labelSx, slate, uiRadii } from "./styleTokens";
import type { SbomServicePatch } from "./SBOMManagementTypes";

export function DeploymentsContent({
  ipAddresses,
  address,
  countryCode,
  editing,
  onUpdate,
  open,
}: {
  ipAddresses: string[];
  address: string;
  countryCode: string;
  editing: boolean;
  onUpdate: (patch: SbomServicePatch) => void;
  open: boolean;
}) {
  const { t } = useTranslation("status", { keyPrefix: "DeploymentsPanel" });
  const { enqueueSnackbar } = useSnackbar();
  const [ipAddressesText, setIpAddressesText] = useState(ipAddresses.join(", "));
  const display = { md: "block", xs: open ? "block" : "none" };
  const normalizedCountryCode = countryCode || "";
  const normalizedAddress = address || "";
  const hasLocation = normalizedCountryCode || normalizedAddress;

  useEffect(() => {
    if (editing) {
      setIpAddressesText(ipAddresses.join(", "));
    }
    // Reset only when entering edit mode; keep the raw comma-separated text while typing.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editing]);

  const emptyText = (
    <Box component="span" sx={{ color: slate[400] }}>
      {t("notSet")}
    </Box>
  );

  if (editing) {
    return (
      <CardContent sx={{ display, minWidth: 0, pb: 1.5, pt: 0, px: 2 }}>
        <Stack sx={{ gap: 2 }}>
          <Box>
            <Typography component="label" sx={labelSx}>
              {t("ipAddresses")}
            </Typography>
            <TextField
              fullWidth
              onChange={(event) => {
                const nextValue = event.target.value;
                setIpAddressesText(nextValue);
                onUpdate({ ipAddresses: normalizeCommaSeparatedValues(nextValue) });
              }}
              placeholder={t("ipAddressesPlaceholder")}
              sx={{ ...fieldSx, mt: 1 }}
              value={ipAddressesText}
            />
          </Box>
          <Box>
            <Typography component="label" sx={labelSx}>
              {t("countryCode")}
            </Typography>
            <TextField
              fullWidth
              inputProps={{ maxLength: 2 }}
              onChange={(event) => {
                onUpdate({ countryCode: event.target.value.toUpperCase() });
              }}
              placeholder={t("countryCodePlaceholder")}
              sx={{ ...fieldSx, mt: 1 }}
              value={normalizedCountryCode}
            />
          </Box>
          <Box>
            <Typography component="label" sx={labelSx}>
              {t("address")}
            </Typography>
            <TextField
              fullWidth
              onChange={(event) => {
                const nextAddress = event.target.value;
                const error = getLengthError(
                  t,
                  nextAddress,
                  maxAssetAddressLengthInHalf,
                  "tooLongAssetAddress",
                );
                if (error) {
                  enqueueSnackbar(error, { variant: "error" });
                  return;
                }

                onUpdate({ address: nextAddress });
              }}
              placeholder={t("addressPlaceholder")}
              sx={{ ...fieldSx, mt: 1 }}
              value={normalizedAddress}
            />
          </Box>
        </Stack>
      </CardContent>
    );
  }

  return (
    <CardContent sx={{ display, minWidth: 0, pb: 1.5, pt: 0, px: 2 }}>
      <Stack sx={{ gap: 2 }}>
        <Box>
          <Typography sx={labelSx}>{t("ipAddresses")}</Typography>
          <Stack sx={{ gap: 1, mt: 1 }}>
            {ipAddresses.length > 0 ? (
              ipAddresses.map((ipAddress, index) => (
                <Box
                  key={`${ipAddress}-${index}`}
                  sx={{
                    bgcolor: slate[50],
                    border: `1px solid ${slate[200]}`,
                    borderRadius: uiRadii.field,
                    color: slate[800],
                    fontSize: 14,
                    fontWeight: 600,
                    p: 1.5,
                  }}
                >
                  {ipAddress}
                </Box>
              ))
            ) : (
              <Box
                sx={{
                  border: `1px dashed ${slate[300]}`,
                  borderRadius: uiRadii.field,
                  color: slate[500],
                  fontSize: 14,
                  p: 2.5,
                  textAlign: "center",
                }}
              >
                {t("noIpAddresses")}
              </Box>
            )}
          </Stack>
        </Box>

        <Box>
          <Typography sx={labelSx}>{t("location")}</Typography>
          {hasLocation ? (
            <Box
              sx={{
                bgcolor: slate[50],
                border: `1px solid ${slate[200]}`,
                borderRadius: uiRadii.field,
                mt: 1,
                p: 1.5,
              }}
            >
              <Stack
                direction="row"
                alignItems="flex-start"
                sx={{ color: slate[800], gap: 1.25, minWidth: 0 }}
              >
                <LocationOnIcon sx={{ color: slate[400], flexShrink: 0, fontSize: 18, mt: 0.25 }} />
                <Stack sx={{ gap: 1, minWidth: 0 }}>
                  <Box>
                    <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
                      {t("countryCode")}
                    </Typography>
                    <Typography sx={{ color: slate[800], fontSize: 14, fontWeight: 600, mt: 0.5 }}>
                      {normalizedCountryCode || emptyText}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
                      {t("address")}
                    </Typography>
                    <Typography
                      sx={{
                        color: slate[800],
                        fontSize: 14,
                        fontWeight: 600,
                        mt: 0.5,
                        overflowWrap: "anywhere",
                      }}
                    >
                      {normalizedAddress || emptyText}
                    </Typography>
                  </Box>
                </Stack>
              </Stack>
            </Box>
          ) : (
            <Typography sx={{ color: slate[400], fontSize: 14, mt: 1 }}>{t("notSet")}</Typography>
          )}
        </Box>
      </Stack>
    </CardContent>
  );
}
