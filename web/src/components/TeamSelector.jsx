import { Add as AddIcon, KeyboardArrowDown as KeyboardArrowDownIcon } from "@mui/icons-material";
import { Box, Button, Divider, ListSubheader, Menu, MenuItem } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { clearATeam } from "../slices/ateam";
import { clearGTeam } from "../slices/gteam";
import { clearPTeam } from "../slices/pteam";
import { setTeamMode } from "../slices/system";
import { teamColor } from "../utils/const";

import { ATeamCreationModal } from "./ATeamCreationModal";
import { GTeamCreationModal } from "./GTeamCreationModal";
import { PTeamCreationModal } from "./PTeamCreationModal";

function textTrim(selector) {
  const maxWordCount = 13;
  const clamp = "…";
  if (selector.length > maxWordCount) {
    selector = selector.substr(0, maxWordCount - 1) + clamp; // remove 1 character
  }
  return selector;
}

export function TeamSelector() {
  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();
  const user = useSelector((state) => state.user.user);
  const teamMode = useSelector((state) => state.system.teamMode);
  const pteamId = useSelector((state) => state.pteam.pteamId);
  const ateamId = useSelector((state) => state.ateam.ateamId);
  const gteamId = useSelector((state) => state.gteam.gteamId);

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const [currentTeamName, setCurrentTeamName] = useState(null);
  const [openPTeamCreationModal, setOpenPTeamCreationModal] = useState(false);
  const [openATeamCreationModal, setOpenATeamCreationModal] = useState(false);
  const [openGTeamCreationModal, setOpenGTeamCreationModal] = useState(false);

  useEffect(() => {
    if (!user) return;
    switch (teamMode) {
      case "pteam":
        setCurrentTeamName(user.pteams?.find((x) => x.pteam_id === pteamId)?.pteam_name);
        break;
      case "ateam":
        setCurrentTeamName(user.ateams?.find((x) => x.ateam_id === ateamId)?.ateam_name);
        break;
      case "gteam":
        setCurrentTeamName(user.gteams?.find((x) => x.gteam_id === gteamId)?.gteam_name);
        break;
      default:
        break;
    }
  }, [teamMode, user, pteamId, ateamId, gteamId]);

  const switchToPTeam = (teamId) => {
    handleClose();
    setCurrentTeamName(user.pteams?.find((x) => x.pteam_id === teamId)?.pteam_name);
    if (teamMode === "pteam") {
      const newParams =
        location.pathname === "/pteam/watching_request"
          ? new URLSearchParams(location.search) // keep request token
          : new URLSearchParams(); // clear params
      newParams.set("pteamId", teamId);
      navigate(location.pathname + "?" + newParams.toString());
    } else {
      dispatch(setTeamMode("pteam"));
      dispatch(clearATeam());
      dispatch(clearGTeam());
      const newParams = new URLSearchParams();
      newParams.set("pteamId", teamId);
      navigate("/?" + newParams.toString());
    }
  };

  const switchToATeam = (teamId) => {
    handleClose();
    setCurrentTeamName(user.ateams?.find((x) => x.ateam_id === teamId)?.ateam_name);
    const newParams = new URLSearchParams();
    newParams.set("ateamId", teamId);
    if (teamMode === "ateam") {
      navigate(location.pathname + "?" + newParams.toString());
    } else {
      dispatch(setTeamMode("ateam"));
      dispatch(clearPTeam());
      dispatch(clearGTeam());
      navigate("/analysis?" + newParams.toString());
    }
  };

  const switchToGTeam = (teamId) => {
    handleClose();
    setCurrentTeamName(user.gteams?.find((x) => x.gteam_id === teamId)?.gteam_name);
    const newParams = new URLSearchParams();
    newParams.set("gteamId", teamId);
    if (teamMode === "gteam") {
      navigate(location.pathname + "?" + newParams.toString());
    } else {
      dispatch(setTeamMode("gteam"));
      dispatch(clearPTeam());
      dispatch(clearATeam());
      navigate("/zone?" + newParams.toString());
    }
  };

  return (
    <>
      <Box>
        <Button
          id="team-selector-button"
          aria-controls={open ? "team-selector-menu" : undefined}
          aria-haspopup="true"
          aria-expanded={open ? "true" : undefined}
          onClick={handleClick}
          variant="outlined"
          sx={{
            textTransform: "none",
            color: teamColor[teamMode].hoverColor,
            border: `1.5px solid ${grey[300]}`,
            "&:hover": {
              bgcolor: grey[100],
              border: `1.5px solid ${grey[300]}`,
            },
          }}
          endIcon={<KeyboardArrowDownIcon />}
        >
          {currentTeamName}
        </Button>
        <Menu
          id="grouped-select"
          label="Grouping"
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
        >
          <ListSubheader sx={{ color: teamColor.pteam.hoverColor }}>Product Team</ListSubheader>
          {user?.pteams &&
            [...user.pteams]
              .sort((a, b) => a.pteam_name.localeCompare(b.pteam_name)) // alphabetically
              .map((pteam) => (
                <MenuItem
                  key={pteam.pteam_id}
                  value={pteam.pteam_id}
                  onClick={() => switchToPTeam(pteam.pteam_id)}
                >
                  {textTrim(pteam.pteam_name)}
                </MenuItem>
              ))}
          <MenuItem onClick={() => setOpenPTeamCreationModal(true)}>
            <AddIcon fontSize="small" />
            Create PTeam
          </MenuItem>
          <Divider />
          <ListSubheader sx={{ color: teamColor.ateam.hoverColor }}>Analysis Team</ListSubheader>
          {user?.ateams &&
            [...user.ateams]
              .sort((a, b) => a.ateam_name.localeCompare(b.ateam_name)) // alphabetically
              .map((ateam) => (
                <MenuItem
                  key={ateam.ateam_id}
                  value={ateam.ateam_name}
                  onClick={() => switchToATeam(ateam.ateam_id)}
                >
                  {textTrim(ateam.ateam_name)}
                </MenuItem>
              ))}
          <MenuItem onClick={() => setOpenATeamCreationModal(true)}>
            <AddIcon fontSize="small" />
            Create ATeam
          </MenuItem>
          <Divider />
          <ListSubheader sx={{ color: teamColor.gteam.hoverColor }}>Governance Team</ListSubheader>
          {user?.gteams &&
            [...user.gteams]
              .sort((a, b) => a.gteam_name.localeCompare(b.gteam_name)) // alphabetically
              .map((gteam) => (
                <MenuItem
                  key={gteam.gteam_id}
                  value={gteam.ateam_name}
                  onClick={() => switchToGTeam(gteam.gteam_id)}
                >
                  {textTrim(gteam.gteam_name)}
                </MenuItem>
              ))}
          <MenuItem onClick={() => setOpenGTeamCreationModal(true)}>
            <AddIcon fontSize="small" />
            Create GTeam
          </MenuItem>
        </Menu>
        <PTeamCreationModal
          open={openPTeamCreationModal}
          setOpen={setOpenPTeamCreationModal}
          closeTeamSelector={handleClose}
        />
        <ATeamCreationModal
          open={openATeamCreationModal}
          setOpen={setOpenATeamCreationModal}
          closeTeamSelector={handleClose}
        />
        <GTeamCreationModal
          open={openGTeamCreationModal}
          setOpen={setOpenGTeamCreationModal}
          closeTeamSelector={handleClose}
        />
      </Box>
    </>
  );
}
