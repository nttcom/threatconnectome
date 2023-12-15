import {
  Key as KeyIcon,
  MoreVert as MoreVertIcon,
  PersonOff as PersonOffIcon,
} from "@mui/icons-material";
import { Button, Dialog, DialogContent, Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { PTeamAuthEditor } from "../components/PTeamAuthEditor";
import { PTeamMemberRemoveModal } from "../components/PTeamMemberRemoveModal";
import { getUser } from "../slices/user";

export function PTeamMemberMenu(props) {
  const { userId, userEmail, isAdmin } = props;

  const [openAuth, setOpenAuth] = useState(false);
  const [openRemove, setOpenRemove] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const dispatch = useDispatch();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const pteam = useSelector((state) => state.pteam.pteam);
  const authorities = useSelector((state) => state.pteam.authorities);
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

  if (!userMe || !pteamId || !pteam || !authorities) return <></>;

  return (
    <>
      <Button
        id={`pteam-member-button-${userId}`}
        aria-controls={open ? `pteam-member-menu-${userId}` : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
      >
        <MoreVertIcon sx={{ color: "gray" }} />
      </Button>
      <Menu
        id={`pteam-member-menu-${userId}`}
        aria-labelledby={`pteam-member-button-${userId}`}
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
            Remove from PTeam
          </MenuItem>
        )}
      </Menu>
      <Dialog open={openAuth}>
        <DialogContent>
          <PTeamAuthEditor
            userId={userId}
            userEmail={userEmail}
            onClose={() => setOpenAuth(false)}
          />
        </DialogContent>
      </Dialog>
      <Dialog open={openRemove}>
        <DialogContent>
          <PTeamMemberRemoveModal
            userId={userId}
            userName={userEmail}
            pteamId={pteamId}
            pteamName={pteam.pteam_name}
            onClose={() => {
              if (userId === userMe.user_id) dispatch(getUser()); // update user.pteam_ids
              setOpenRemove(false);
            }}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

PTeamMemberMenu.propTypes = {
  userId: PropTypes.string.isRequired,
  userEmail: PropTypes.string.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
