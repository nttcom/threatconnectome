import {
  ErrorOutline as ErrorOutlineIcon,
  TaskAlt as TaskAltIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  IconButton,
  TextField,
  Typography,
  FormControl,
  OutlinedInput,
  InputAdornment,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getATeam } from "../slices/ateam";
import { getUser } from "../slices/user";
import {
  updateATeam,
  checkSlack as postCheckSlack,
  checkFs as postCheckFs,
  getFsInfo,
} from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

import CheckButton from "./CheckButton";

export default function ATeamGeneralSetting(props) {
  const { show } = props;
  const [ateamName, setATeamName] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [edittingSlackUrl, setEdittingSlackUrl] = useState(false);
  const [slackUrl, setSlackUrl] = useState("");
  const [checkSlack, setCheckSlack] = useState(false);
  const [slackMessage, setSlackMessage] = useState();
  const [flashsenseUrl, setFlashsenseUrl] = useState("");
  const [checkFlashsense, setCheckFlashsense] = useState(false);
  const [flashsenseMessage, setFlashsenseMessage] = useState();

  const { enqueueSnackbar } = useSnackbar();

  const ateamId = useSelector((state) => state.ateam.ateamId);
  const ateam = useSelector((state) => state.ateam.ateam);

  const dispatch = useDispatch();

  useEffect(() => {
    async function fetchFsInfo() {
      const fsInfo = await getFsInfo().then((response) => response.data);
      setFlashsenseUrl(fsInfo.api_url);
    }

    if (!ateam) dispatch(getATeam(ateamId));
    fetchFsInfo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (ateam) {
      setATeamName(ateam.ateam_name);
      setContactInfo(ateam.contact_info);
      setSlackUrl(ateam.slack_webhook_url);
    }
    setCheckFlashsense(false);
    setFlashsenseMessage();
  }, [show, ateam]);

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

  const handleUpdateATeam = async () => {
    const ateamInfo = {
      ateam_name: ateamName,
      contact_info: contactInfo,
      slack_webhook_url: slackUrl,
    };
    await updateATeam(ateamId, ateamInfo)
      .then(() => {
        dispatch(getATeam(ateamId));
        dispatch(getUser());
        enqueueSnackbar("update ateam info succeeded", { variant: "success" });
      })
      .catch((error) => operationError(error));
  };

  const handleCheckSlack = async () => {
    setCheckSlack(true);
    setSlackMessage();
    await postCheckSlack({ slack_webhook_url: slackUrl })
      .then(() => {
        setCheckSlack(false);
        setSlackMessage(connectSuccessMessage);
      })
      .catch((error) => {
        setCheckSlack(false);
        setSlackMessage(connectFailMessage(error));
      });
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
          id="outlined-basic"
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
          id="outlined-basic"
          size="small"
          value={contactInfo}
          onChange={(event) => setContactInfo(event.target.value)}
          variant="outlined"
          sx={{ marginRight: "10px", minWidth: "800px" }}
        />
      </Box>

      <Box mb={1}>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          Notification
        </Typography>
      </Box>
      <Box mb={1} sx={{ ml: "40px" }}>
        <Typography sx={{ fontWeight: 400 }} mb={1}>
          Slack Incoming Webhook URL
        </Typography>
        <Box display="flex" alignItems="center">
          <FormControl
            sx={{ marginRight: "10px", minWidth: "675px" }}
            variant="outlined"
            size="small"
          >
            <OutlinedInput
              id="outlined-adornment-password"
              type={edittingSlackUrl ? "text" : "password"}
              autocomplete="new-password" // to avoid autocomplete by browser
              value={slackUrl}
              onChange={(event) => setSlackUrl(event.target.value)}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setEdittingSlackUrl(!edittingSlackUrl)}
                    edge="end"
                  >
                    {edittingSlackUrl ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              }
            />
          </FormControl>
          <CheckButton handleClick={handleCheckSlack} isLoading={checkSlack} />
        </Box>
        <Box mt={1}>{slackMessage}</Box>
      </Box>

      <Box>
        <Typography sx={{ fontWeight: 900 }} mb={1}>
          Connected Flashsense server
        </Typography>
        <Box display="flex" alignItems="center">
          <Typography sx={{ color: grey[700], minWidth: "720px" }} mr={1} mb={1}>
            {flashsenseUrl}
          </Typography>
          <CheckButton handleClick={handleCheckFlashsense} isLoading={checkFlashsense} />
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
