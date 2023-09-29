import { DoDisturbAlt as DoDisturbAltIcon, MoreVert as MoreVertIcon } from "@mui/icons-material";
import { Box, Button, Menu, MenuItem, Modal } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch } from "react-redux";

import ATeamWatchingStop from "../components/ATeamWatchingStop";
import { getATeam } from "../slices/ateam";
import { sxModal } from "../utils/const";

export default function ATeamWatchingMenu(props) {
  const { ateam, watchingPteamId, watchingPteamName, isAdmin } = props;

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
      <Modal open={openRemove}>
        <Box sx={sxModal}>
          <ATeamWatchingStop
            watchingPteamId={watchingPteamId}
            watchingPteamName={watchingPteamName}
            ateamId={ateam.ateam_id}
            ateamName={ateam.ateam_name}
            onClose={() => {
              dispatch(getATeam(ateam.ateam_id)); // update ateam.pteams
              setOpenRemove(false);
            }}
          />
        </Box>
      </Modal>
    </>
  );
}

ATeamWatchingMenu.propTypes = {
  ateam: PropTypes.object.isRequired,
  watchingPteamId: PropTypes.string.isRequired,
  watchingPteamName: PropTypes.string.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};
