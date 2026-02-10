import {
  Key as KeyIcon,
  MoreVert as MoreVertIcon,
  PersonOff as PersonOffIcon,
} from "@mui/icons-material";
import { Dialog, DialogContent, IconButton, Menu, MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetPTeamQuery, useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString, checkAdmin } from "../../utils/func";

import { PTeamAuthEditor } from "./PTeamAuthEditor";
import { PTeamMemberRemoveModal } from "./PTeamMemberRemoveModal";

export function PTeamMemberMenu(props) {
  const { pteamId, memberUserId, userEmail, isTargetMemberAdmin } = props;
  const { t } = useTranslation("pteam", { keyPrefix: "PTeamMemberMenu" });

  const [openAuth, setOpenAuth] = useState(false);
  const [openRemove, setOpenRemove] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const skip = useSkipUntilAuthUserIsReady() || !pteamId;
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });
  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery({ path: { pteam_id: pteamId } }, { skip });

  if (skip) return <></>;
  if (userMeError)
    throw new APIError(errorToString(userMeError), {
      api: "getUserMe",
    });
  if (userMeIsLoading) return <>{t("nowLoadingUserInfo")}</>;
  if (pteamError)
    throw new APIError(errorToString(pteamError), {
      api: "getPTeam",
    });
  if (pteamIsLoading) return <>{t("nowLoadingTeam")}</>;

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
      <IconButton
        id={`pteam-member-button-${memberUserId}`}
        aria-controls={open ? `pteam-member-menu-${memberUserId}` : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
      >
        <MoreVertIcon sx={{ color: "gray" }} />
      </IconButton>
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
          {t("authorities")}
        </MenuItem>
        {(isCurrentUserAdmin || memberUserId === userMe.user_id) && (
          <MenuItem onClick={handleRemoveMember}>
            <PersonOffIcon sx={{ mr: 1 }} />
            {t("removeFromTeam")}
          </MenuItem>
        )}
      </Menu>
      <Dialog open={openAuth} onClose={() => setOpenAuth(false)}>
        <DialogContent>
          <PTeamAuthEditor
            pteamId={pteamId}
            memberUserId={memberUserId}
            userEmail={userEmail}
            isTargetMemberAdmin={isTargetMemberAdmin}
            isCurrentUserAdmin={isCurrentUserAdmin}
            onClose={() => setOpenAuth(false)}
          />
        </DialogContent>
      </Dialog>
      {(isCurrentUserAdmin || memberUserId === userMe.user_id) && (
        <Dialog open={openRemove} onClose={() => setOpenRemove(false)}>
          <PTeamMemberRemoveModal
            memberUserId={memberUserId}
            userName={userEmail}
            pteamId={pteamId}
            pteamName={pteam.pteam_name}
            onClose={() => setOpenRemove(false)}
          />
        </Dialog>
      )}
    </>
  );
}

PTeamMemberMenu.propTypes = {
  pteamId: PropTypes.string.isRequired,
  memberUserId: PropTypes.string.isRequired,
  userEmail: PropTypes.string.isRequired,
  isTargetMemberAdmin: PropTypes.bool.isRequired,
};
