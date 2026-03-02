import { createTheme } from "@mui/material/styles";

declare module "@mui/material/styles" {
  interface TypeBackground {
    subtle: string;
  }
}

const theme = createTheme({
  palette: {
    background: {
      subtle: "rgba(0, 0, 0, 0.04)",
    },
  },
});

export default theme;
