import { ErrorOutline as ErrorOutlineIcon, TaskAlt as TaskAltIcon } from "@mui/icons-material";
import { Box, Button, TextField, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getGTeam } from "../slices/gteam";
import { getUser } from "../slices/user";
import { updateGTeam, checkFs as postCheckFs, getFsInfo } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

import { CheckButton } from "./CheckButton";

export function GTeamGeneralSetting(props) {
  const { show } = props;
  const [gteamName, setGTeamName] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [flashsenseUrl, setFlashsenseUrl] = useState("");
  const [checkFlashsense, setCheckFlashsense] = useState(false);
  const [flashsenseMessage, setFlashsenseMessage] = useState();

  const { enqueueSnackbar } = useSnackbar();

  const gteamId = useSelector((state) => state.gteam.gteamId);
  const gteam = useSelector((state) => state.gteam.gteam);

  const dispatch = useDispatch();

  useEffect(() => {
    async function fetchFsInfo() {
      const fsInfo = await getFsInfo().then((response) => response.data);
      setFlashsenseUrl(fsInfo.api_url);
    }
    if (!gteam) dispatch(getGTeam(gteamId));
    fetchFsInfo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (gteam) {
      setGTeamName(gteam.gteam_name);
      setContactInfo(gteam.contact_info);
    }
    setCheckFlashsense(false);
    setFlashsenseMessage();
  }, [show, gteam]);

  const operationError = (error) => {
    const resp = error.response;
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  const connectSuccessMessage = () => {
    return (
      <Box display="flex" sx={{ color: "success.main" }}>
        <TaskAltIcon />
        <Typography>Connection successful </Typography>
      </Box>
    );
  };

  const connectFailMessage = (error) => {
    return (
      <Box display="flex" sx={{ color: "error.main" }}>
        <ErrorOutlineIcon />
        <Typography>Connection failed. Reason: {error.response?.data.detail} </Typography>
      </Box>
    );
  };

  const handleUpdateGTeam = async () => {
    const gteamInfo = { gteam_name: gteamName, contact_info: contactInfo };
    await updateGTeam(gteamId, gteamInfo)
      .then(() => {
        dispatch(getGTeam(gteamId));
        dispatch(getUser());
        enqueueSnackbar("update gteam info succeeded", { variant: "success" });
      })
      .catch((error) => operationError(error));
  };

  const handleCheckFlashsense = async () => {
    setCheckFlashsense(true);
    setFlashsenseMessage();
    await postCheckFs()
      .then(() => {
        setCheckFlashsense(false);
        setFlashsenseMessage(connectSuccessMessage);
      })
      .catch((error) => {
        setCheckFlashsense(false);
        setFlashsenseMessage(connectFailMessage(error));
      });
  };

  return (
    <Box>
      <Box mb={4}>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          GTeam name
        </Typography>
        <TextField
          id="outlined-basic"
          size="small"
          value={gteamName}
          onChange={(event) => setGTeamName(event.target.value)}
          variant="outlined"
          sx={{ marginRight: "10px", minWidth: "800px" }}
        />
      </Box>
      <Box mb={4}>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          Contact Info
        </Typography>
        <TextField
          id="outlined-basic"
          size="small"
          value={contactInfo}
          onChange={(event) => setContactInfo(event.target.value)}
          variant="outlined"
          sx={{ marginRight: "10px", minWidth: "800px" }}
        />
      </Box>
      <Box>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          Connected Flashsense server
        </Typography>
        <Box display="flex" alignItems="center">
          <Typography sx={{ color: grey[700], minWidth: "720px" }} mr={1} mb={1}>
            {flashsenseUrl}
          </Typography>
          <CheckButton onHandleClick={handleCheckFlashsense} isLoading={checkFlashsense} />
        </Box>
      </Box>
      <Box mb={4}>{flashsenseMessage}</Box>
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <Button
          onClick={() => handleUpdateGTeam("gteamName")}
          sx={{ ...modalCommonButtonStyle, ml: 1 }}
        >
          Update
        </Button>
      </Box>
    </Box>
  );
}
GTeamGeneralSetting.propTypes = {
  show: PropTypes.bool.isRequired,
};
