import { Add as AddIcon, KeyboardArrowDown as KeyboardArrowDownIcon } from "@mui/icons-material";
import { Box, Button, Divider, ListSubheader, Menu, MenuItem } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetUserMeQuery } from "../services/tcApi";
import { LocationReader } from "../utils/LocationReader";
import { teamColor } from "../utils/const";
import { errorToString } from "../utils/func";

import { PTeamCreateModal } from "./PTeamCreateModal";

function textTrim(selector) {
  const maxWordCount = 13;
  const clamp = "…";
  if (selector.length > maxWordCount) {
    selector = selector.substr(0, maxWordCount - 1) + clamp; // remove 1 character
  }
  return selector;
}

export function TeamSelector() {
  const location = useLocation();
  const navigate = useNavigate();

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  const handleClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const [currentTeamName, setCurrentTeamName] = useState(null);
  const [openPTeamCreationModal, setOpenPTeamCreationModal] = useState(false);
  const locationReader = useMemo(() => new LocationReader(location), [location]);

  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  useEffect(() => {
    if (!userMe) return;
    if (locationReader.isPTeamMode()) {
      setCurrentTeamName(
        userMe.pteams?.find((x) => x.pteam_id === locationReader.getPTeamId())?.pteam_name,
      );
    }
  }, [userMe, locationReader]);

  if (skip) return <></>;
  if (userMeError) return <>{`Cannot get UserInfo: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const switchToPTeam = (teamId) => {
    handleClose();
    setCurrentTeamName(userMe.pteams?.find((x) => x.pteam_id === teamId)?.pteam_name);

    if (locationReader.isPTeamMode()) {
      if (locationReader.isTagPage() || locationReader.isPTeamInvitationPage()) {
        const newParams = new URLSearchParams();
        newParams.set("pteamId", teamId);
        navigate("/?" + newParams);
      }
    } else {
      const newParams = new URLSearchParams();
      newParams.set("pteamId", teamId);
      navigate("/?" + newParams.toString());
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
            color: teamColor[locationReader.getTeamMode()].hoverColor,
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
        </Menu>
        <PTeamCreateModal
          open={openPTeamCreationModal}
          onSetOpen={setOpenPTeamCreationModal}
          onCloseTeamSelector={handleClose}
        />
      </Box>
    </>
  );
}
