import { DoDisturbAlt as DoDisturbAltIcon, MoreVert as MoreVertIcon } from "@mui/icons-material";
import { Button, Dialog, Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { PTeamWatcherRemoveModal } from "../components/PTeamWatcherRemoveModal";

export function PTeamWatcherMenu(props) {
  const { pteam, watcherAteamId, watcherAteamName, isAdmin } = props;

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
            id={`pteam-monitor-button-${watcherAteamId}`}
            aria-controls={open ? `pteam-monitor-menu-${watcherAteamId}` : undefined}
            aria-haspopup="true"
            aria-expanded={open ? "true" : undefined}
            onClick={handleClick}
          >
            <MoreVertIcon sx={{ color: "gray" }} />
          </Button>
          <Menu
            id={`pteam-monitor-menu-${watcherAteamId}`}
            aria-labelledby={`pteam-monitor-button-${watcherAteamId}`}
            anchorEl={anchorEl}
            open={open}
            onClose={handleClose}
            anchorOrigin={{ vertical: "top", horizontal: "left" }}
            transformOrigin={{ vertical: "top", horizontal: "left" }}
          >
            <MenuItem onClick={handleRemoveMember}>
              <DoDisturbAltIcon sx={{ mr: 1 }} />
              Remove this watcher
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
        <PTeamWatcherRemoveModal
          watcherAteamId={watcherAteamId}
          watcherAteamName={watcherAteamName}
          pteamId={pteam.pteam_id}
          pteamName={pteam.pteam_name}
          onClose={() => setOpenRemove(false)}
        />
      </Dialog>
    </>
  );
}

PTeamWatcherMenu.propTypes = {
  pteam: PropTypes.object.isRequired,
  watcherAteamId: PropTypes.string.isRequired,
  watcherAteamName: PropTypes.string.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
