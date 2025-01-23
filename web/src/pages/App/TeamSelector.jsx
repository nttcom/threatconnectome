import { Add as AddIcon, KeyboardArrowDown as KeyboardArrowDownIcon } from "@mui/icons-material";
import { Box, Button, Menu, MenuItem } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { LocationReader } from "../../utils/LocationReader";
import { drawerParams } from "../../utils/const";
import { errorToString } from "../../utils/func";

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

  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined);

  useEffect(() => {
    if (!userMe) return;
    setCurrentTeamName(
      userMe.pteam_roles?.find((x) => x.pteam.pteam_id === locationReader.getPTeamId())?.pteam
        .pteam_name,
    );
  }, [userMe, locationReader]);

  if (userMeError) throw new APIError(errorToString(userMeError), { api: "getUserMe" });
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const switchToPTeam = (teamId) => {
    handleClose();
    setCurrentTeamName(
      userMe.pteam_roles?.find((x) => x.pteam.pteam_id === teamId)?.pteam.pteam_name,
    );
    const newParams = new URLSearchParams();
    newParams.set("pteamId", teamId);
    navigate("/?" + newParams.toString());
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
            color: drawerParams.hoverColor,
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
          {userMe?.pteam_roles &&
            [...userMe.pteam_roles]
              .sort((a, b) => a.pteam.pteam_name.localeCompare(b.pteam.pteam_name)) // alphabetically
              .map((pteam_role) => (
                <MenuItem
                  key={pteam_role.pteam.pteam_id}
                  value={pteam_role.pteam.pteam_id}
                  onClick={() => switchToPTeam(pteam_role.pteam.pteam_id)}
                >
                  {textTrim(pteam_role.pteam.pteam_name)}
                </MenuItem>
              ))}
          <MenuItem onClick={() => setOpenPTeamCreationModal(true)}>
            <AddIcon fontSize="small" />
            Create Team
          </MenuItem>
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
