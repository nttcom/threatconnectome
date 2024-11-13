import { DoDisturbAlt as DoDisturbAltIcon, MoreVert as MoreVertIcon } from "@mui/icons-material";
import { Button, Dialog, Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { ATeamWatchingStop } from "../components/ATeamWatchingStop";

export function ATeamWatchingMenu(props) {
  const { ateam, watchingPteamId, watchingPteamName, isAdmin } = props;

  const [openRemove, setOpenRemove] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const handleRemoveMember = () => {
    handleClose();
    setOpenRemove(true);
  };

  return (
    <>
      {isAdmin ? (
        <>
          <Button
            id={`ateam-monitor-button-${watchingPteamId}`}
            aria-controls={open ? `ateam-monitor-menu-${watchingPteamId}` : undefined}
            aria-haspopup="true"
            aria-expanded={open ? "true" : undefined}
            onClick={handleClick}
          >
            <MoreVertIcon sx={{ color: "gray" }} />
          </Button>
          <Menu
            id={`ateam-monitor-menu-${watchingPteamId}`}
            aria-labelledby={`ateam-monitor-button-${watchingPteamId}`}
            anchorEl={anchorEl}
            open={open}
            onClose={handleClose}
            anchorOrigin={{ vertical: "top", horizontal: "left" }}
            transformOrigin={{ vertical: "top", horizontal: "left" }}
          >
            <MenuItem onClick={handleRemoveMember}>
              <DoDisturbAltIcon sx={{ mr: 1 }} />
              Stop Watching
            </MenuItem>
          </Menu>
        </>
      ) : (
        <></>
      )}
      <Dialog
        open={openRemove}
        onClose={() => {
          setOpenRemove(false);
        }}
      >
        <ATeamWatchingStop
          watchingPteamId={watchingPteamId}
          watchingPteamName={watchingPteamName}
          ateamId={ateam.ateam_id}
          ateamName={ateam.ateam_name}
          onClose={() => {
            setOpenRemove(false);
          }}
        />
      </Dialog>
    </>
  );
}

ATeamWatchingMenu.propTypes = {
  ateam: PropTypes.object.isRequired,
  watchingPteamId: PropTypes.string.isRequired,
  watchingPteamName: PropTypes.string.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
