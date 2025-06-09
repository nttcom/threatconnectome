import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import LogoutIcon from "@mui/icons-material/Logout";
import SettingsIcon from "@mui/icons-material/Settings";
import {
  Divider,
  IconButton,
  ListItemIcon,
  ListItemText,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import { useState } from "react";
import { useDispatch } from "react-redux";

import { useAuth, useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { tcApi, useGetUserMeQuery } from "../../../services/tcApi";
import { setAuthUserIsReady, setRedirectedFrom } from "../../../slices/auth";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";

import { AccountSettings } from "./AccountSettings";

export function UserMenu() {
  const dispatch = useDispatch();
  const { signOut } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [accountSettingOpen, setAccountSettingOpen] = useState(false);
  const theme = useTheme();
  const matches = useMediaQuery(theme.breakpoints.up("sm"));

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  if (skip) return <></>;
  if (userMeError)
    throw new APIError(errorToString(userMeError), {
      api: "getUserMe",
    });
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const openUserMenu = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const handleAccountSetting = () => {
    setAccountSettingOpen(true);
    setAnchorEl(null);
  };
  const handleLogout = async () => {
    dispatch(tcApi.util.resetApiState()); // reset RTKQ
    dispatch(setAuthUserIsReady(false));
    dispatch(setRedirectedFrom({}));
    await signOut();
  };

  return (
    <>
      {matches ? (
        <Button
          aria-label="user menu"
          onClick={handleClick}
          startIcon={<AccountCircleIcon />}
          sx={{ maxWidth: 400 }}
        >
          <Typography
            variant="button"
            sx={{ textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }}
          >
            {userMe.email}
          </Typography>
        </Button>
      ) : (
        <IconButton aria-label="user menu" onClick={handleClick} color="primary" size="large">
          <AccountCircleIcon />
        </IconButton>
      )}
      <Menu
        anchorEl={anchorEl}
        open={openUserMenu}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
      >
        <MenuItem onClick={handleAccountSetting}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => {
            handleLogout();
            handleClose();
          }}
        >
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Logout</ListItemText>
        </MenuItem>
      </Menu>
      <AccountSettings
        accountSettingOpen={accountSettingOpen}
        setAccountSettingOpen={setAccountSettingOpen}
        userMe={userMe}
      />
    </>
  );
}
