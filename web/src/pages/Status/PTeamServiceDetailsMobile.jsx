import { Box, Card, CardContent, CardMedia } from "@mui/material";

export function PTeamServiceDetailsMobile() {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
      <Card sx={{ width: 300 }}>
        <CardMedia component="img" image="/images/720x480.png" sx={{ aspectRatio: "3 / 2" }} />
        <CardContent>PTeamServiceDetailsMobile</CardContent>
      </Card>
    </Box>
  );
}
