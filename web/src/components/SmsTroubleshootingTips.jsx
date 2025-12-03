import { Box, Typography } from "@mui/material";

export function SmsTroubleshootingTips() {
  const resolvedTips = [
    "The phone number entered is accurate.",
    "Your device has sufficient network coverage and is not in airplane mode.",
    "SMS filtering, blocking settings, or carrier restrictions are not preventing delivery.",
    "The message has not been placed in your spam or junk folder.",
  ];

  return (
    <Box
      sx={{
        width: "100%",
        mt: 1,
        pl: 1,
      }}
    >
      <Typography variant="body2" sx={{ ml: 0.5, fontWeight: 600 }} gutterBottom>
        If the verification SMS does not arrive, please verify the following:
      </Typography>
      <Box
        component="ol"
        sx={{
          pl: 4,
          m: 0,
          fontSize: (theme) => theme.typography.body2.fontSize,
        }}
      >
        {resolvedTips.map((tip) => (
          <Box
            component="li"
            key={tip}
            sx={{
              mb: 0.5,
            }}
          >
            {tip}
          </Box>
        ))}
      </Box>
    </Box>
  );
}
