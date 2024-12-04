import { ArrowDropDown as ArrowDropDownIcon } from "@mui/icons-material";
import { Button, Box, Menu, MenuItem, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { IconContext } from "react-icons";
import { MdOutlineTopic } from "react-icons/md";

import { TopicModal } from "./TopicModal";

export function PTeamStatusMenu(props) {
  const { presetTagId, presetParentTagId, pteamId } = props;
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <Button
        id="status-menu-button"
        aria-controls={open ? "customized-menu" : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        variant="contained"
        disableElevation
        sx={{
          bgcolor: grey[100],
          color: "black",
          textTransform: "none",
          "&:hover": {
            bgcolor: grey[300],
          },
        }}
        onClick={handleClick}
        endIcon={<ArrowDropDownIcon />}
      >
        Menu
      </Button>
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
      >
        <MenuItem
          onClick={() => {
            setModalOpen(true);
            handleClose();
          }}
          sx={{ mg: 10 }}
        >
          <Box display="flex" flexDirection="column" alignItems="center">
            <IconContext.Provider value={{ color: "black", size: "20px" }}>
              <MdOutlineTopic />
            </IconContext.Provider>
            <Typography variant="caption">New Topics</Typography>
          </Box>
        </MenuItem>
      </Menu>
      <TopicModal
        open={modalOpen}
        onSetOpen={setModalOpen}
        presetTagId={presetTagId}
        presetParentTagId={presetParentTagId}
        pteamId={pteamId}
      />
    </>
  );
}

PTeamStatusMenu.propTypes = {
  presetTagId: PropTypes.string,
  presetParentTagId: PropTypes.string,
  pteamId: PropTypes.string.isRequired,
};
