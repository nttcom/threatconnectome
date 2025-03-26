import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import LogoutIcon from "@mui/icons-material/Logout";
import SettingsIcon from "@mui/icons-material/Settings";
import { Divider, ListItemIcon, ListItemText } from "@mui/material";
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import React, { useState } from "react";
import { useDispatch } from "react-redux";

import { useAuth } from "../../hooks/auth";
import { tcApi } from "../../services/tcApi";
import { setAuthUserIsReady, setRedirectedFrom } from "../../slices/auth";

import SettingsDialog from "./SettingsDialog";

export function UserMenu() {
  const dispatch = useDispatch();
  const { signOut } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const [settingOpen, setSettingOpen] = useState(false);
  const handleClickSettingOpen = () => {
    setSettingOpen(true);
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
      <Button onClick={handleClick} startIcon={<AccountCircleIcon />}>
        sample@example.com
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={open}
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
        <MenuItem onClick={handleClickSettingOpen}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Setting</ListItemText>
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
      <SettingsDialog open={settingOpen} setOpen={setSettingOpen} />
    </>
  );
}
