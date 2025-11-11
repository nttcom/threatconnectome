import { styled } from "@mui/material/styles";

import { drawerWidth } from "../../utils/const";

interface MainProps {
  open: boolean;
}

const Main = styled("main", { shouldForwardProp: (prop) => prop !== "open" })<MainProps>(
  ({ theme, open }) => ({
    display: "flex",
    justifyContent: "center",
    padding: theme.spacing(1),
    transition: theme.transitions.create("margin", {
      duration: theme.transitions.duration.leavingScreen,
      easing: theme.transitions.duration.sharp,
    }),
    ...(open && {
      marginLeft: `${drawerWidth}px`,
      transition: theme.transitions.create("margin", {
        duration: theme.transitions.duration.enteringScreen,
        easing: theme.transitions.easing.easeOut,
      }),
    }),
  }),
);

export { Main };
