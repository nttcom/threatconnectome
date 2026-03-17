import { createTheme } from "@mui/material/styles";

declare module "@mui/material/styles" {
  interface TypeBackground {
    soft: string;
  }
}

const theme = createTheme({
  palette: {
    background: {
      soft: "rgba(0, 0, 0, 0.04)",
    },
  },
});

export default theme;
