import { ErrorOutline as ErrorOutlineIcon, TaskAlt as TaskAltIcon } from "@mui/icons-material";
import { Box, Button, TextField, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";

import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useUpdateATeamMutation, useGetATeamQuery } from "../services/tcApi";
import { checkFs as postCheckFs, getFsInfo } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";
import { errorToString } from "../utils/func";

import { CheckButton } from "./CheckButton";

export function ATeamGeneralSetting(props) {
  const { show } = props;
  const [ateamName, setATeamName] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [slackUrl, setSlackUrl] = useState("");
  const [flashsenseUrl, setFlashsenseUrl] = useState("");
  const [checkFlashsense, setCheckFlashsense] = useState(false);
  const [flashsenseMessage, setFlashsenseMessage] = useState();

  const { enqueueSnackbar } = useSnackbar();
  const [updateATeam] = useUpdateATeamMutation();

  const ateamId = useSelector((state) => state.ateam.ateamId);
  const skip = useSkipUntilAuthTokenIsReady();

  const {
    data: ateam,
    error: ateamError,
    isLoading: ateamIsLoading,
  } = useGetATeamQuery(ateamId, { skip });

  useEffect(() => {
    async function fetchFsInfo() {
      const fsInfo = await getFsInfo().then((response) => response.data);
      setFlashsenseUrl(fsInfo.api_url);
    }

    if (!ateam) fetchFsInfo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (ateam) {
      setATeamName(ateam.ateam_name);
      setContactInfo(ateam.contact_info);
      setSlackUrl(ateam.alert_slack.webhook_url);
    }
    setCheckFlashsense(false);
    setFlashsenseMessage();
  }, [show, ateam]);

  if (skip) return <></>;
  if (ateamError) return <>{`Cannot get Ateam: ${errorToString(ateamError)}`}</>;
  if (ateamIsLoading) return <>Now loading Ateam...</>;

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

  const handleUpdateATeam = async () => {
    const ateamInfo = {
      ateam_name: ateamName,
      contact_info: contactInfo,
      alert_slack: { enable: true, webhook_url: slackUrl }, //todo change enable status
    };
    await updateATeam({ ateamId: ateamId, data: ateamInfo })
      .unwrap()
      .then(() => {
        enqueueSnackbar("update ateam info succeeded", { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" }),
      );
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
          ATeam name
        </Typography>
        <TextField
          size="small"
          value={ateamName}
          onChange={(event) => setATeamName(event.target.value)}
          variant="outlined"
          sx={{ marginRight: "10px", minWidth: "800px" }}
        />
      </Box>
      <Box mb={4}>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          Contact Info
        </Typography>
        <TextField
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
        <Button onClick={() => handleUpdateATeam()} sx={{ ...modalCommonButtonStyle, ml: 1 }}>
          Update
        </Button>
      </Box>
    </Box>
  );
}
ATeamGeneralSetting.propTypes = {
  show: PropTypes.bool.isRequired,
};
