import {
  AccountCircle as AccountCircleIcon,
  Groups as GroupsIcon,
  Home as HomeIcon,
  Topic as TopicIcon,
} from "@mui/icons-material";
import {
  Drawer as MuiDrawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import React from "react";
import { useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { LocationReader } from "../utils/LocationReader";
import { drawerWidth, drawerParams } from "../utils/const";

const DrawerHeader = styled("div")(({ theme }) => ({
  alignItems: "center",
  display: "flex",
  justifyContent: "center",
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

export function Drawer() {
  const location = useLocation();
  const locationReader = new LocationReader(location);
  const navigate = useNavigate();

  const system = useSelector((state) => state.system);

  const StyledListItemIcon = styled(ListItemIcon)({
    color: "white",
  });

  const StyledListItemButton = styled(ListItemButton)({
    "&:hover": {
      backgroundColor: drawerParams.hoverColor,
    },
    "&.Mui-selected": {
      backgroundColor: drawerParams.hoverColor,
      "&:hover": {
        backgroundColor: drawerParams.hoverColor,
      },
    },
  });

  const queryParams = new URLSearchParams(location.search).toString();

  const handleNavigateTop = () => {
    navigate("/?" + queryParams);
  };

  const drawerTitle = "Threatconnectome";

  return (
    <MuiDrawer
      anchor="left"
      open={system.drawerOpen}
      variant="persistent"
      sx={{
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          boxSizing: "border-box",
          width: drawerWidth,
        },
      }}
      PaperProps={{
        sx: {
          backgroundColor: drawerParams.mainColor,
          color: "white",
        },
      }}
    >
      <DrawerHeader>
        <Typography onClick={handleNavigateTop} variant="h7" sx={{ fontWeight: 700 }}>
          {drawerTitle}
        </Typography>
      </DrawerHeader>
      <List>
        <>
          <StyledListItemButton
            onClick={() => navigate("/?" + queryParams)}
            selected={locationReader.isStatusPage()}
          >
            <StyledListItemIcon>
              <HomeIcon />
            </StyledListItemIcon>
            <ListItemText>Status</ListItemText>
          </StyledListItemButton>
          <StyledListItemButton
            onClick={() => navigate("/pteam?" + queryParams)}
            selected={locationReader.isPTeamPage()}
          >
            <StyledListItemIcon>
              <GroupsIcon />
            </StyledListItemIcon>
            <ListItemText>PTeam</ListItemText>
          </StyledListItemButton>
        </>
        {/* Topics */}
        <StyledListItemButton
          onClick={() => navigate("/topics?" + queryParams)}
          selected={locationReader.isTopicsPage()}
        >
          <StyledListItemIcon>
            <TopicIcon />
          </StyledListItemIcon>
          <ListItemText>Topics</ListItemText>
        </StyledListItemButton>
        {/* Account */}
        <StyledListItemButton
          onClick={() => navigate("/account?" + queryParams)}
          selected={locationReader.isAccountPage()}
        >
          <StyledListItemIcon>
            <AccountCircleIcon />
          </StyledListItemIcon>
          <ListItemText>Account</ListItemText>
        </StyledListItemButton>
      </List>
    </MuiDrawer>
  );
}
