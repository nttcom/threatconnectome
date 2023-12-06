import {
  Key as KeyIcon,
  MoreVert as MoreVertIcon,
  PersonOff as PersonOffIcon,
} from "@mui/icons-material";
import { Button, Dialog, DialogContent, Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import GTeamAuthEditor from "../components/GTeamAuthEditor";
import GTeamMemberRemove from "../components/GTeamMemberRemove";
import { getUser } from "../slices/user";

export default function GTeamMemberMenu(props) {
  const { userId, userEmail, isAdmin } = props;

  const [openAuth, setOpenAuth] = useState(false);
  const [openRemove, setOpenRemove] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const dispatch = useDispatch();

  const gteamId = useSelector((state) => state.gteam.gteamId);
  const gteam = useSelector((state) => state.gteam.gteam);
  const authorities = useSelector((state) => state.gteam.authorities);
  const userMe = useSelector((state) => state.user.user);

  const handleClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);
  const handleAuthorities = () => {
    handleClose();
    setOpenAuth(true);
  };
  const handleRemoveMember = () => {
    handleClose();
    setOpenRemove(true);
  };

  if (!userMe || !gteamId || !gteam || !authorities) return <></>;

  return (
    <>
      <Button
        id={`gteam-member-button-${userId}`}
        aria-controls={open ? `gteam-member-menu-${userId}` : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
      >
        <MoreVertIcon sx={{ color: "gray" }} />
      </Button>
      <Menu
        id={`gteam-member-menu-${userId}`}
        aria-labelledby={`gteam-member-button-${userId}`}
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        anchorOrigin={{ vertical: "top", horizontal: "left" }}
        transformOrigin={{ vertical: "top", horizontal: "left" }}
      >
        <MenuItem onClick={handleAuthorities}>
          <KeyIcon sx={{ mr: 1 }} />
          Authorities
        </MenuItem>
        {(isAdmin || userId === userMe.user_id) && (
          <MenuItem onClick={handleRemoveMember}>
            <PersonOffIcon sx={{ mr: 1 }} />
            Remove from GTeam
          </MenuItem>
        )}
      </Menu>
      <Dialog open={openAuth}>
        <DialogContent>
          <GTeamAuthEditor
            userId={userId}
            userEmail={userEmail}
            onClose={() => setOpenAuth(false)}
          />
        </DialogContent>
      </Dialog>
      <Dialog open={openRemove}>
        <DialogContent>
          <GTeamMemberRemove
            userId={userId}
            userName={userEmail}
            gteamId={gteamId}
            gteamName={gteam.gteam_name}
            onClose={() => {
              if (userId === userMe.user_id) dispatch(getUser()); // update user.gteams
              setOpenRemove(false);
            }}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

GTeamMemberMenu.propTypes = {
  userId: PropTypes.string.isRequired,
  userEmail: PropTypes.string.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
