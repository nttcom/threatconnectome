import { Add as AddIcon, KeyboardArrowDown as KeyboardArrowDownIcon } from "@mui/icons-material";
import { Box, Button, Divider, ListSubheader, Menu, MenuItem } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useParams, useNavigate } from "react-router-dom";

import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetUserMeQuery } from "../services/tcApi";
import { clearATeam } from "../slices/ateam";
import { clearPTeam } from "../slices/pteam";
import { setTeamMode } from "../slices/system";
import { teamColor } from "../utils/const";
import { errorToString } from "../utils/func";

import { ATeamCreateModal } from "./ATeamCreateModal";
import { PTeamCreateModal } from "./PTeamCreateModal";

function textTrim(selector) {
  const maxWordCount = 13;
  const clamp = "…";
  if (selector.length > maxWordCount) {
    selector = selector.substr(0, maxWordCount - 1) + clamp; // remove 1 character
  }
  return selector;
}

export function TeamSelector(props) {
  const { ateamId, pteamId } = props;

  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();
  const teamMode = useSelector((state) => state.system.teamMode);

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const [currentTeamName, setCurrentTeamName] = useState(null);
  const [openPTeamCreationModal, setOpenPTeamCreationModal] = useState(false);
  const [openATeamCreationModal, setOpenATeamCreationModal] = useState(false);
  const { tagId } = useParams();

  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  useEffect(() => {
    if (!userMe) return;
    switch (teamMode) {
      case "pteam":
        setCurrentTeamName(userMe.pteams?.find((x) => x.pteam_id === pteamId)?.pteam_name);
        break;
      case "ateam":
        setCurrentTeamName(userMe.ateams?.find((x) => x.ateam_id === ateamId)?.ateam_name);
        break;
      default:
        break;
    }
  }, [teamMode, userMe, pteamId, ateamId]);

  if (skip) return <></>;
  if (userMeError) return <>{`Cannot get UserInfo: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const switchToPTeam = (teamId) => {
    handleClose();
    setCurrentTeamName(userMe.pteams?.find((x) => x.pteam_id === teamId)?.pteam_name);

    if (teamMode === "pteam") {
      if (tagId || location.pathname === "/ateam/join") {
        const newParams = new URLSearchParams();
        newParams.set("pteamId", teamId);
        navigate("/?" + newParams);
      } else {
        const newParams =
          location.pathname === "/pteam/watching_request"
            ? new URLSearchParams(location.search) // keep request token
            : new URLSearchParams(); // clear params
        newParams.set("pteamId", teamId);
        navigate(location.pathname + "?" + newParams.toString());
      }
    } else {
      dispatch(setTeamMode("pteam"));
      dispatch(clearATeam());
      const newParams = new URLSearchParams();
      newParams.set("pteamId", teamId);
      navigate("/?" + newParams.toString());
    }
  };

  const switchToATeam = (teamId) => {
    handleClose();
    setCurrentTeamName(userMe.ateams?.find((x) => x.ateam_id === teamId)?.ateam_name);
    const newParams = new URLSearchParams();
    newParams.set("ateamId", teamId);
    if (teamMode === "ateam") {
      navigate(location.pathname + "?" + newParams.toString());
    } else {
      dispatch(setTeamMode("ateam"));
      dispatch(clearPTeam());
      navigate("/analysis?" + newParams.toString());
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
          {userMe?.pteams &&
            [...userMe.pteams]
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
          {userMe?.ateams &&
            [...userMe.ateams]
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
        </Menu>
        <PTeamCreateModal
          open={openPTeamCreationModal}
          onSetOpen={setOpenPTeamCreationModal}
          onCloseTeamSelector={handleClose}
        />
        <ATeamCreateModal
          open={openATeamCreationModal}
          onOpen={setOpenATeamCreationModal}
          onCloseTeamSelector={handleClose}
        />
      </Box>
    </>
  );
}
TeamSelector.propTypes = {
  ateamId: PropTypes.string,
  pteamId: PropTypes.string,
};
