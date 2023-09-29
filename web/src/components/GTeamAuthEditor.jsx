import {
  CheckBox as CheckedIcon,
  CheckBoxOutlineBlank as UnCheckedIcon,
  CheckBoxOutlined as CheckedOutlinedIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Divider,
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
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getGTeamAuth, getGTeamAuthInfo } from "../slices/gteam";
import { updateGTeamAuth } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export default function GTeamAuthEditor(props) {
  const { userId, userEmail, onClose } = props;

  const [newAuth, setNewAuth] = useState({ user: [], member: [], others: [] });
  const [gteamAuth, setGTeamAuth] = useState({});
  const [editable, setEditable] = useState(false);
  const [uuidOthers, setUuidOthers] = useState(null);
  const [uuidMember, setUuidMember] = useState(null);
  const [pseudoEdit, setPseudoEdit] = useState(userId ? false : true);

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();

  const gteamId = useSelector((state) => state.gteam.gteamId);
  const authorities = useSelector((state) => state.gteam.authorities);
  const authInfo = useSelector((state) => state.gteam.authInfo);
  const userMe = useSelector((state) => state.user.user);

  useEffect(() => {
    if (!gteamId) return;
    if (!authorities) {
      dispatch(getGTeamAuth(gteamId));
      return;
    }
    setGTeamAuth(
      authorities.reduce(
        (ret, val) => ({
          ...ret,
          [val.user_id]: val.authorities,
        }),
        {}
      )
    );
  }, [dispatch, gteamId, authorities]);

  useEffect(() => {
    if (!gteamAuth || !uuidMember || !uuidOthers) return;
    setNewAuth({
      user: gteamAuth[userId] ?? [],
      member: gteamAuth[uuidMember] ?? [],
      others: gteamAuth[uuidOthers] ?? [],
    });
  }, [gteamAuth, userId, uuidMember, uuidOthers]);

  useEffect(() => {
    if (!userMe) return;
    setEditable((gteamAuth[userMe.user_id] ?? []).includes("admin"));
  }, [gteamAuth, userMe]);

  useEffect(() => {
    if (!authInfo) {
      dispatch(getGTeamAuthInfo());
      return;
    }
    authInfo.pseudo_uuids?.forEach((elm) => {
      if (elm.name === "others") setUuidOthers(elm.uuid);
      else if (elm.name === "member") setUuidMember(elm.uuid);
    });
  }, [authInfo, dispatch]);

  const switchPseudoEdit = () => {
    setNewAuth({
      user: gteamAuth[userId] ?? [],
      member: gteamAuth[uuidMember] ?? [],
      others: gteamAuth[uuidOthers] ?? [],
    });
    setPseudoEdit(!pseudoEdit);
  };

  const handleSave = async (targets) => {
    function onSuccess(success) {
      dispatch(getGTeamAuth(gteamId));
      enqueueSnackbar("Update gteam authority succeeded", { variant: "success" });
    }
    function onError(error) {
      enqueueSnackbar(`Update gteam authority failed: ${error.response?.data?.detail}`, {
        variant: "error",
      });
    }
    const request = pseudoEdit
      ? [
          { user_id: uuidOthers, authorities: newAuth.others },
          { user_id: uuidMember, authorities: newAuth.member },
        ]
      : [{ user_id: userId, authorities: newAuth.user }];
    await updateGTeamAuth(gteamId, request)
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  const authRow = (auth) => {
    const authOthers = newAuth.others.includes(auth.enum);
    const authMember = newAuth.member.includes(auth.enum);
    const authUser = newAuth.user.includes(auth.enum);
    const sxGray = { color: "gray" };
    const sxBlack = { color: "black" };
    const sxBlue = { color: "#1976d2" }; // default primary color
    const genCallback = (target) => () =>
      setNewAuth({
        ...newAuth,
        [target]: newAuth[target].includes(auth.enum)
          ? newAuth[target].filter((item) => item !== auth.enum)
          : [...newAuth[target], auth.enum],
      });
    const othersCell = (
      <TableCell
        align="center"
        onClick={pseudoEdit ? genCallback("others") : undefined}
        sx={{ cursor: pseudoEdit ? "pointer" : undefined }}
      >
        {authOthers ? (
          <CheckedIcon sx={pseudoEdit ? sxBlue : sxGray} fontSize="small" />
        ) : (
          <UnCheckedIcon sx={pseudoEdit ? sxBlue : sxGray} fontSize="small" />
        )}
        {newAuth.others.includes(auth.enum) !== (gteamAuth[uuidOthers] ?? []).includes(auth.enum) &&
          "*"}
      </TableCell>
    );
    const memberCell = (
      <TableCell
        align="center"
        onClick={pseudoEdit ? genCallback("member") : undefined}
        sx={{ cursor: pseudoEdit ? "pointer" : undefined }}
      >
        {authMember ? (
          <CheckedIcon sx={pseudoEdit ? sxBlue : sxBlack} fontSize="small" />
        ) : authOthers ? (
          <CheckedOutlinedIcon sx={pseudoEdit ? sxBlue : sxGray} fontSize="small" />
        ) : (
          <UnCheckedIcon sx={pseudoEdit ? sxBlue : sxGray} fontSize="small" />
        )}
        {newAuth.member.includes(auth.enum) !== (gteamAuth[uuidMember] ?? []).includes(auth.enum) &&
          "*"}
      </TableCell>
    );
    const userCell = pseudoEdit ? (
      <></>
    ) : (
      <TableCell
        align="center"
        onClick={editable ? genCallback("user") : undefined}
        sx={{ cursor: editable ? "pointer" : undefined }}
      >
        {authUser ? (
          <CheckedIcon sx={sxBlue} fontSize="small" />
        ) : authMember ? (
          <CheckedOutlinedIcon sx={sxBlack} fontSize="small" />
        ) : authOthers ? (
          <CheckedOutlinedIcon sx={sxGray} fontSize="small" />
        ) : (
          <UnCheckedIcon sx={sxGray} fontSize="small" />
        )}
        {newAuth.user.includes(auth.enum) !== (gteamAuth[userId] ?? []).includes(auth.enum) && "*"}
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
  };

  const updated = () =>
    pseudoEdit
      ? newAuth.others.slice().sort().toString() !==
          (gteamAuth[uuidOthers] ?? []).slice().sort().toString() ||
        newAuth.member.slice().sort().toString() !==
          (gteamAuth[uuidMember] ?? []).slice().sort().toString()
      : newAuth.user.slice().sort().toString() !==
        (gteamAuth[userId] ?? []).slice().sort().toString();

  return userMe && newAuth.user && authInfo && authorities && gteamAuth ? (
    <>
      <Typography variant="h5">Authority: {pseudoEdit ? "member & others" : userEmail}</Typography>
      <Divider sx={{ my: 1 }} />
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
          <TableBody>{authInfo.authorities.map((auth) => authRow(auth))}</TableBody>
        </Table>
      </TableContainer>
      <Box display="flex" mt={2}>
        {editable && userId && (
          <Button onClick={switchPseudoEdit} sx={modalCommonButtonStyle}>
            {pseudoEdit ? `Edit ${userEmail}` : "Edit Pseudo"}
          </Button>
        )}
        <Box flexGrow={1} />
        {onClose && (
          <Button onClick={onClose} sx={modalCommonButtonStyle}>
            {editable && updated() ? "Cancel" : "Close"}
          </Button>
        )}
        {editable && (
          <Button
            onClick={handleSave}
            disabled={!updated()}
            sx={{ ...modalCommonButtonStyle, ml: 1 }}
          >
            Update
          </Button>
        )}
      </Box>
    </>
  ) : (
    <></>
  );
}

GTeamAuthEditor.propTypes = {
  userId: PropTypes.string,
  userEmail: PropTypes.string,
  onClose: PropTypes.func,
};
