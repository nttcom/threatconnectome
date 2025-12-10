import UpdateIcon from "@mui/icons-material/Update";
import { orange } from "@mui/material/colors";

import { Box } from "@mui/material";

export function ActionTypeIcon() {
  return (
    <Box sx={{ mr: 0.5, mt: 0.5 }}>
      <UpdateIcon sx={{ color: orange[900], fontSize: 25 }} />
    </Box>
  );
}
