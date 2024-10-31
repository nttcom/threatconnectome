import {
  CheckBox as CheckedIcon,
  CheckBoxOutlineBlank as UnCheckedIcon,
  CheckBoxOutlined as CheckedOutlinedIcon,
  Close as CloseIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";

import dialogStyle from "../cssModule/dialog.module.css";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import {
  useGetPTeamAuthQuery,
  useGetPTeamAuthInfoQuery,
  useGetUserMeQuery,
  useUpdatePTeamAuthMutation,
} from "../services/tcApi";
import { errorToString } from "../utils/func";

function AuthRow(props) {
  const { auth, newAuth, currentAuth, editable, pseudoEdit, onSwitchTarget } = props;

  const authOthers = newAuth.others.includes(auth.enum);
  const authMember = newAuth.member.includes(auth.enum);
  const authUser = newAuth.user.includes(auth.enum);
  const fixedSx = (isPseudo, enable) => ({
    color: editable && isPseudo === pseudoEdit ? "#1976d2" : enable ? "black" : "gray",
  });

  const othersCell = (
    <TableCell
      align="center"
      onClick={editable && pseudoEdit ? onSwitchTarget("others") : undefined}
      sx={{ cursor: editable && pseudoEdit ? "pointer" : undefined }}
    >
      {authOthers ? (
        <CheckedIcon sx={fixedSx(true, true)} fontSize="small" />
      ) : (
        <UnCheckedIcon sx={fixedSx(true, false)} fontSize="small" />
      )}
      {newAuth.others.includes(auth.enum) !== currentAuth.others.includes(auth.enum) && "*"}
    </TableCell>
  );
  const memberCell = (
    <TableCell
      align="center"
      onClick={editable && pseudoEdit ? onSwitchTarget("member") : undefined}
      sx={{ cursor: editable && pseudoEdit ? "pointer" : undefined }}
    >
      {authMember ? (
        <CheckedIcon sx={fixedSx(true, true)} fontSize="small" />
      ) : authOthers ? (
        <CheckedOutlinedIcon sx={fixedSx(true, true)} fontSize="small" />
      ) : (
        <UnCheckedIcon sx={fixedSx(true, false)} fontSize="small" />
      )}
      {newAuth.member.includes(auth.enum) !== currentAuth.member.includes(auth.enum) && "*"}
    </TableCell>
  );
  const userCell = pseudoEdit ? (
    <></>
  ) : (
    <TableCell
      align="center"
      onClick={editable ? onSwitchTarget("user") : undefined}
      sx={{ cursor: editable ? "pointer" : undefined }}
    >
      {authUser ? (
        <CheckedIcon sx={fixedSx(false, true)} fontSize="small" />
      ) : authMember ? (
        <CheckedOutlinedIcon sx={fixedSx(false, true)} fontSize="small" />
      ) : authOthers ? (
        <CheckedOutlinedIcon sx={fixedSx(false, true)} fontSize="small" />
      ) : (
        <UnCheckedIcon sx={fixedSx(false, false)} fontSize="small" />
      )}
      {newAuth.user.includes(auth.enum) !== currentAuth.user.includes(auth.enum) && "*"}
    </TableCell>
  );
  return (
    <TableRow key={auth.enum}>
      {othersCell}
      {memberCell}
      {userCell}
      <TableCell>{auth.name}</TableCell>
      <TableCell>{auth.desc}</TableCell>
    </TableRow>
  );
}

AuthRow.propTypes = {
  auth: PropTypes.object.isRequired,
  newAuth: PropTypes.object.isRequired,
  currentAuth: PropTypes.object.isRequired,
  editable: PropTypes.bool.isRequired,
  pseudoEdit: PropTypes.bool.isRequired,
  onSwitchTarget: PropTypes.func.isRequired,
};

function PTeamAuthEditorMain(props) {
  // wrap me to make sure currentAuth is ready as initial value for useState
  const { pteamId, userId, userEmail, onClose, authInfo, uuidOthers, uuidMember, currentAuth } =
    props;

  const [newAuth, setNewAuth] = useState(currentAuth);
  const [pseudoEdit, setPseudoEdit] = useState(userId ? false : true);

  const [updatePTeamAuth] = useUpdatePTeamAuthMutation();

  const { enqueueSnackbar } = useSnackbar();

  const editable = currentAuth.me.includes("admin");

  const switchPseudoEdit = () => {
    setNewAuth(currentAuth); // reset
    setPseudoEdit(!pseudoEdit);
  };

  const handleSave = async (targets) => {
    function onSuccess(success) {
      enqueueSnackbar("Update pteam authority succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Update pteam authority failed: ${errorToString(error)}`, {
        variant: "error",
      });
    }
    const data = pseudoEdit
      ? [
          { user_id: uuidOthers, authorities: newAuth.others },
          { user_id: uuidMember, authorities: newAuth.member },
        ]
      : [{ user_id: userId, authorities: newAuth.user }];
    await updatePTeamAuth({ pteamId, data })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  const handleUpdateAuth = (auth) => (target) => () =>
    setNewAuth({
      ...newAuth,
      [target]: newAuth[target].includes(auth.enum)
        ? newAuth[target].filter((item) => item !== auth.enum)
        : [...newAuth[target], auth.enum],
    });

  const updated = () =>
    pseudoEdit
      ? newAuth.others.slice().sort().toString() !== currentAuth.others.slice().sort().toString() ||
        newAuth.member.slice().sort().toString() !== currentAuth.member.slice().sort().toString()
      : newAuth.user.slice().sort().toString() !== currentAuth.user.slice().sort().toString();

  return (
    <>
      <Box display="flex" flexDirection="row">
        <Typography className={dialogStyle.dialog_title}>
          Authority: {pseudoEdit ? "member & others" : userEmail}
        </Typography>
        <Box flexGrow={1} />
        {onClose && (
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        )}
      </Box>
      <TableContainer>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              {["Others", "Member", ...(pseudoEdit ? [] : ["User"])].map((name) => (
                <TableCell key={name} sx={{ width: "10%", fontWeight: 900 }} align="center">
                  {name}
                </TableCell>
              ))}
              <TableCell sx={{ width: "30%", fontWeight: 900 }}>Authority</TableCell>
              <TableCell sx={{ fontWeight: 900 }}>Description</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {authInfo.authorities.map((auth) => (
              <AuthRow
                key={auth.enum}
                auth={auth}
                newAuth={newAuth}
                currentAuth={currentAuth}
                editable={editable}
                pseudoEdit={pseudoEdit}
                onSwitchTarget={handleUpdateAuth(auth)}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Box display="flex" mt={2}>
        {editable && userId && (
          <Button onClick={switchPseudoEdit} className={dialogStyle.submit_btn}>
            {pseudoEdit ? `Edit ${userEmail}` : "Edit Pseudo"}
          </Button>
        )}
        <Box flexGrow={1} />
        {editable && (
          <Button onClick={handleSave} disabled={!updated()} className={dialogStyle.submit_btn}>
            Update
          </Button>
        )}
      </Box>
    </>
  );
}

PTeamAuthEditorMain.propTypes = {
  pteamId: PropTypes.string.isRequired,
  userId: PropTypes.string,
  userEmail: PropTypes.string,
  onClose: PropTypes.func,
  authInfo: PropTypes.object.isRequired,
  uuidOthers: PropTypes.string.isRequired,
  uuidMember: PropTypes.string.isRequired,
  currentAuth: PropTypes.object.isRequired,
  userMe: PropTypes.object.isRequired,
};

export function PTeamAuthEditor(props) {
  const { pteamId, userId, userEmail, onClose } = props;

  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });
  const {
    data: authInfo,
    error: authInfoError,
    isLoading: authInfoIsLoading,
  } = useGetPTeamAuthInfoQuery(undefined, { skip });
  const {
    data: pteamAuth,
    error: pteamAuthError,
    isLoading: pteamAuthIsLoading,
  } = useGetPTeamAuthQuery(pteamId, { skip: skip || !pteamId });

  if (skip || !pteamId) return <></>;
  if (userMeError) return <>{`Cannot get UserInfo: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;
  if (authInfoError) return <>{`Cannot get PTeam: ${errorToString(authInfoError)}`}</>;
  if (authInfoIsLoading) return <>Now loading Auth Info...</>;
  if (pteamAuthError) return <>{`Cannot get Authorities: ${errorToString(pteamAuthError)}`}</>;
  if (pteamAuthIsLoading) return <>Now loading Authorities...</>;

  const uuidOthers = authInfo.pseudo_uuids.find((elm) => elm.name === "others").uuid;
  const uuidMember = authInfo.pseudo_uuids.find((elm) => elm.name === "member").uuid;
  const currentAuth = {
    user: pteamAuth[userId] ?? [],
    member: pteamAuth[uuidMember] ?? [],
    others: pteamAuth[uuidOthers] ?? [],
    me: pteamAuth[userMe.user_id] ?? [],
  };

  return (
    <PTeamAuthEditorMain
      pteamId={pteamId}
      userId={userId}
      userEmail={userEmail}
      onClose={onClose}
      authInfo={authInfo}
      uuidOthers={uuidOthers}
      uuidMember={uuidMember}
      currentAuth={currentAuth}
      userMe={userMe}
    />
  );
}

PTeamAuthEditor.propTypes = {
  pteamId: PropTypes.string.isRequired,
  userId: PropTypes.string,
  userEmail: PropTypes.string,
  onClose: PropTypes.func,
};
