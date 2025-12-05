import UpdateIcon from "@mui/icons-material/Update";
import { Box } from "@mui/material";
import { orange } from "@mui/material/colors";
import { IconContext } from "react-icons";

export function ActionTypeIcon() {
  return (
    <Box sx={{ mr: 0.5, mt: 0.5 }}>
      <>
        <Box>
          <IconContext.Provider value={{ color: orange[900], size: "25px" }}>
            <UpdateIcon />
          </IconContext.Provider>
        </Box>
      </>
    </Box>
  );
}
