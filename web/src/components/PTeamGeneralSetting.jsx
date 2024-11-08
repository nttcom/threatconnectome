import { ErrorOutline as ErrorOutlineIcon, TaskAlt as TaskAltIcon } from "@mui/icons-material";
import { Box, Button, Divider, TextField, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import { useUpdatePTeamMutation } from "../services/tcApi";
import { checkFs as postCheckFs, getFsInfo } from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";
import { errorToString } from "../utils/func";

import { CheckButton } from "./CheckButton";

export function PTeamGeneralSetting(props) {
  const { show, pteam } = props;

  const [pteamName, setPTeamName] = useState(pteam.pteam_name);
  const [contactInfo, setContactInfo] = useState(pteam.contact_info);
  const [flashsenseUrl, setFlashsenseUrl] = useState("");
  const [checkFlashsense, setCheckFlashsense] = useState(false);
  const [flashsenseMessage, setFlashsenseMessage] = useState("");

  const [updatePTeam] = useUpdatePTeamMutation();

  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    async function fetchFsInfo() {
      const fsInfo = await getFsInfo().then((response) => response.data);
      setFlashsenseUrl(fsInfo.api_url);
    }

    fetchFsInfo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (show) {
      setCheckFlashsense(false);
      setFlashsenseMessage();
    }
  }, [show]);

  const operationError = (error) =>
    enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" });

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

  const handleUpdatePTeam = async () => {
    const data = {
      pteam_name: pteamName,
      contact_info: contactInfo,
    };
    await updatePTeam({ pteamId: pteam.pteam_id, data })
      .unwrap()
      .then(() => {
        enqueueSnackbar("update pteam info succeeded", { variant: "success" });
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
          PTeam name
        </Typography>
        <TextField
          size="small"
          value={pteamName}
          onChange={(event) => setPTeamName(event.target.value)}
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
      <Divider />
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <Button onClick={() => handleUpdatePTeam()} sx={{ ...modalCommonButtonStyle, ml: 1 }}>
          Update
        </Button>
      </Box>
    </Box>
  );
}
PTeamGeneralSetting.propTypes = {
  show: PropTypes.bool.isRequired,
  pteam: PropTypes.object.isRequired,
};
