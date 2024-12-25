import {
  Key as KeyIcon,
  MoreVert as MoreVertIcon,
  PersonOff as PersonOffIcon,
} from "@mui/icons-material";
import { Button, Dialog, DialogContent, Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { useSkipUntilAuthTokenIsReady } from "../../hooks/auth";
import { useGetPTeamQuery, useGetUserMeQuery } from "../../services/tcApi";
import { errorToString, checkAdmin } from "../../utils/func";

import { PTeamAuthEditor } from "./PTeamAuthEditor";
import { PTeamMemberRemoveModal } from "./PTeamMemberRemoveModal";

export function PTeamMemberMenu(props) {
  const { pteamId, memberUserId, userEmail, isCurrentMemberAdmin } = props;

  const [openAuth, setOpenAuth] = useState(false);
  const [openRemove, setOpenRemove] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const skip = useSkipUntilAuthTokenIsReady() || !pteamId;
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });
  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, { skip });

  if (skip) return <></>;
  if (userMeError) return <>{`Cannot get userInfo: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;
  if (pteamError) return <>{`Cannot get PTeam: ${errorToString(pteamError)}`}</>;
  if (pteamIsLoading) return <>Now loading PTeam...</>;

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

  const isCurrentUserAdmin = checkAdmin(userMe, pteamId);

  return (
    <>
      <Button
        id={`pteam-member-button-${memberUserId}`}
        aria-controls={open ? `pteam-member-menu-${memberUserId}` : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
      >
        <MoreVertIcon sx={{ color: "gray" }} />
      </Button>
      <Menu
        id={`pteam-member-menu-${memberUserId}`}
        aria-labelledby={`pteam-member-button-${memberUserId}`}
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
        {(isCurrentUserAdmin || memberUserId === userMe.user_id) && (
          <MenuItem onClick={handleRemoveMember}>
            <PersonOffIcon sx={{ mr: 1 }} />
            Remove from PTeam
          </MenuItem>
        )}
      </Menu>
      <Dialog open={openAuth} onClose={() => setOpenAuth(false)}>
        <DialogContent>
          <PTeamAuthEditor
            pteamId={pteamId}
            memberUserId={memberUserId}
            userEmail={userEmail}
            isCurrentMemberAdmin={isCurrentMemberAdmin}
            onClose={() => setOpenAuth(false)}
          />
        </DialogContent>
      </Dialog>
      <Dialog open={openRemove} onClose={() => setOpenRemove(false)}>
        <PTeamMemberRemoveModal
          memberUserId={memberUserId}
          userName={userEmail}
          pteamId={pteamId}
          pteamName={pteam.pteam_name}
          onClose={() => setOpenRemove(false)}
        />
      </Dialog>
    </>
  );
}

PTeamMemberMenu.propTypes = {
  pteamId: PropTypes.string.isRequired,
  memberUserId: PropTypes.string.isRequired,
  userEmail: PropTypes.string.isRequired,
  isCurrentMemberAdmin: PropTypes.bool.isRequired,
};
