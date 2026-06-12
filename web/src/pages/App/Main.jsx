import { styled } from "@mui/material/styles";

const Main = styled("main")(({ theme }) => ({
  display: "flex",
  justifyContent: "center",
  padding: theme.spacing(1),
}));

export { Main };
