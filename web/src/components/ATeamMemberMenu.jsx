import {
  Key as KeyIcon,
  MoreVert as MoreVertIcon,
  PersonOff as PersonOffIcon,
} from "@mui/icons-material";
import { Box, Button, Menu, MenuItem, Modal } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import ATeamAuthEditor from "../components/ATeamAuthEditor";
import ATeamMemberRemove from "../components/ATeamMemberRemove";
import { getUser } from "../slices/user";
import { sxModal } from "../utils/const";

export default function ATeamMemberMenu(props) {
  const { userId, userEmail, isAdmin } = props;

  const [openAuth, setOpenAuth] = useState(false);
  const [openRemove, setOpenRemove] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const dispatch = useDispatch();

  const ateamId = useSelector((state) => state.ateam.ateamId);
  const ateam = useSelector((state) => state.ateam.ateam);
  const authorities = useSelector((state) => state.ateam.authorities);
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

  const sxAuthModal = {
    ...sxModal,
    minWidth: "800px",
  };
  const sxRemoveModal = {
    ...sxModal,
  };

  if (!userMe || !ateamId || !ateam || !authorities) return <></>;

  return (
    <>
      <Button
        id={`ateam-member-button-${userId}`}
        aria-controls={open ? `ateam-member-menu-${userId}` : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
      >
        <MoreVertIcon sx={{ color: "gray" }} />
      </Button>
      <Menu
        id={`ateam-member-menu-${userId}`}
        aria-labelledby={`ateam-member-button-${userId}`}
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
            Remove from ateam
          </MenuItem>
        )}
      </Menu>
      <Modal open={openAuth}>
        <Box sx={sxAuthModal}>
          <ATeamAuthEditor
            userId={userId}
            userEmail={userEmail}
            onClose={() => setOpenAuth(false)}
          />
        </Box>
      </Modal>
      <Modal open={openRemove}>
        <Box sx={sxRemoveModal}>
          <ATeamMemberRemove
            userId={userId}
            userName={userEmail}
            ateamId={ateamId}
            ateamName={ateam.ateam_name}
            onClose={() => {
              if (userId === userMe.user_id) dispatch(getUser()); // update user.ateams
              setOpenRemove(false);
            }}
          />
        </Box>
      </Modal>
    </>
  );
}

ATeamMemberMenu.propTypes = {
  userId: PropTypes.string.isRequired,
  userEmail: PropTypes.string.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
