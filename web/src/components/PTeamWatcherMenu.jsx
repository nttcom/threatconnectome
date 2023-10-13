import { DoDisturbAlt as DoDisturbAltIcon, MoreVert as MoreVertIcon } from "@mui/icons-material";
import { Box, Button, Menu, MenuItem, Modal } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch } from "react-redux";

import PTeamWatcherRemove from "../components/PTeamWatcherRemove";
import { getPTeam } from "../slices/pteam";
import { sxModal } from "../utils/const";

export default function PTeamWatcherMenu(props) {
  const { pteam, watcherAteamId, watcherAteamName, isAdmin } = props;

  const [openRemove, setOpenRemove] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const dispatch = useDispatch();

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
      <Modal open={openRemove}>
        <Box sx={sxModal}>
          <PTeamWatcherRemove
            watcherAteamId={watcherAteamId}
            watcherAteamName={watcherAteamName}
            pteamId={pteam.pteam_id}
            pteamName={pteam.pteam_name}
            onClose={() => {
              dispatch(getPTeam(pteam.pteam_id)); // update pteam.pteams
              setOpenRemove(false);
            }}
          />
        </Box>
      </Modal>
    </>
  );
}

PTeamWatcherMenu.propTypes = {
  pteam: PropTypes.object.isRequired,
  watcherAteamId: PropTypes.string.isRequired,
  watcherAteamName: PropTypes.string.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
