import {
  ErrorOutline as ErrorOutlineIcon,
  TaskAlt as TaskAltIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Divider,
  IconButton,
  MenuItem,
  Select,
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

import { getPTeam } from "../slices/pteam";
import { getUser } from "../slices/user";
import {
  updatePTeam,
  checkSlack as postCheckSlack,
  checkFs as postCheckFs,
  getFsInfo,
} from "../utils/api";
import { threatImpactName, threatImpactProps, modalCommonButtonStyle } from "../utils/const";

import { CheckButton } from "./CheckButton";

export function PTeamGeneralSetting(props) {
  const { show } = props;
  const [pteamName, setPTeamName] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [edittingSlackUrl, setEdittingSlackUrl] = useState(false);
  const [slackUrl, setSlackUrl] = useState("");
  const [alertImpact, setAlertImpact] = useState(1);
  const [checkSlack, setCheckSlack] = useState(false);
  const [slackMessage, setSlackMessage] = useState();
  const [flashsenseUrl, setFlashsenseUrl] = useState("");
  const [checkFlashsense, setCheckFlashsense] = useState(false);
  const [flashsenseMessage, setFlashsenseMessage] = useState();

  const { enqueueSnackbar } = useSnackbar();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const pteam = useSelector((state) => state.pteam.pteam);

  const dispatch = useDispatch();

  useEffect(() => {
    async function fetchFsInfo() {
      const fsInfo = await getFsInfo().then((response) => response.data);
      setFlashsenseUrl(fsInfo.api_url);
    }

    if (!pteam) dispatch(getPTeam(pteamId));
    fetchFsInfo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (pteam) {
      setPTeamName(pteam.pteam_name);
      setContactInfo(pteam.contact_info);
      setSlackUrl(pteam.alert_slack.webhook_url);
      setAlertImpact(pteam.alert_threat_impact);
    }
    setEdittingSlackUrl(false);
    setCheckSlack(false);
    setSlackMessage();
    setCheckFlashsense(false);
    setFlashsenseMessage();
  }, [show, pteam]);

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

  const handleUpdatePTeam = async () => {
    const pteamInfo = {
      pteam_name: pteamName,
      contact_info: contactInfo,
      alert_slack: { enable: true, webhook_url: slackUrl }, //todo change enable status
      alert_threat_impact: alertImpact,
    };
    await updatePTeam(pteamId, pteamInfo)
      .then(() => {
        dispatch(getPTeam(pteamId));
        dispatch(getUser());
        enqueueSnackbar("update pteam info succeeded", { variant: "success" });
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
          PTeam name
        </Typography>
        <TextField
          id="pteam-name-field"
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
          id="contact-info-field"
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
              autoComplete="new-password" // to avoid autocomplete by browser
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
          <CheckButton onHandleClick={handleCheckSlack} isLoading={checkSlack} />
        </Box>
        <Box mt={1}>{slackMessage}</Box>
      </Box>
      <Box mb={4} sx={{ ml: "40px" }}>
        <Typography sx={{ fontWeight: 400 }} mb={1}>
          Alert threshold
        </Typography>
        <Select
          value={alertImpact}
          onChange={(event) => setAlertImpact(Number(event.target.value))}
          sx={{ marginRight: "10px", minWidth: "760px" }}
        >
          {Object.keys(threatImpactName).map((key) => (
            <MenuItem key={key} value={key}>
              {key}: {threatImpactProps[threatImpactName[key]].chipLabel}
            </MenuItem>
          ))}
        </Select>
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
};
