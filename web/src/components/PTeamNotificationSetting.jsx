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
  FormControl,
  FormControlLabel,
  IconButton,
  InputAdornment,
  MenuItem,
  Select,
  Switch,
  Typography,
  OutlinedInput,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getPTeam } from "../slices/pteam";
import { getUser } from "../slices/user";
import {
  updatePTeam,
  checkSlack as postCheckSlack,
  checkMail as postCheckMail,
} from "../utils/api";
import { modalCommonButtonStyle, sortedSSVCPriorities, ssvcPriorityProps } from "../utils/const";

import { CheckButton } from "./CheckButton";

export function PTeamNotificationSetting(props) {
  const { show } = props;
  const [edittingSlackUrl, setEdittingSlackUrl] = useState(false);
  const [slackUrl, setSlackUrl] = useState("");
  const [slackEnable, setSlackEnable] = useState(false);
  const [mailAddress, setMailAddress] = useState("");
  const [mailEnable, setMailEnable] = useState(false);
  const [alertThreshold, setAlertThreshold] = useState("");
  const [checkSlack, setCheckSlack] = useState(false);
  const [checkEmail, setCheckEmail] = useState(false);
  const [slackMessage, setSlackMessage] = useState();
  const [emailMessage, setEmailMessage] = useState();

  const { enqueueSnackbar } = useSnackbar();

  const pteamId = useSelector((state) => state.pteam.pteamId);
  const pteam = useSelector((state) => state.pteam.pteam);

  const dispatch = useDispatch();

  useEffect(() => {
    if (pteam) {
      setSlackUrl(pteam.alert_slack.webhook_url);
      setSlackEnable(pteam.alert_slack.enable);
      setMailAddress(pteam.alert_mail.address);
      setMailEnable(pteam.alert_mail.enable);
      setAlertThreshold(pteam.alert_ssvc_priority);
    }
    setEdittingSlackUrl(false);
    setCheckSlack(false);
    setSlackMessage();
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
      alert_slack: { enable: slackEnable, webhook_url: slackUrl },
      alert_mail: { enable: mailEnable, address: mailAddress },
      alert_ssvc_priority: alertThreshold,
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

  const handleCheckMail = async () => {
    setCheckEmail(true);
    setEmailMessage();
    await postCheckMail({ email: mailAddress })
      .then(() => {
        setCheckEmail(false);
        setEmailMessage(connectSuccessMessage);
      })
      .catch((error) => {
        setCheckEmail(false);
        setEmailMessage(connectFailMessage(error));
      });
  };

  const AndroidSwitch = styled(Switch)(({ theme }) => ({
    padding: 8,
    "& .MuiSwitch-track": {
      borderRadius: 22 / 2,
      "&:before, &:after": {
        content: "''",
        position: "absolute",
        top: "50%",
        transform: "translateY(-50%)",
        width: 16,
        height: 16,
      },
      "&:before": {
        backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
          theme.palette.getContrastText(theme.palette.primary.main),
        )}" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>")`,
        left: 12,
      },
      "&:after": {
        backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
          theme.palette.getContrastText(theme.palette.primary.main),
        )}" d="M19,13H5V11H19V13Z" /></svg>")`,
        right: 12,
      },
    },
    "& .MuiSwitch-thumb": {
      boxShadow: "none",
      width: 16,
      height: 16,
      margin: 2,
    },
  }));

  return (
    <Box>
      <Box mb={2}>
        <Typography sx={{ fontWeight: 400 }} mb={1}>
          Alert threshold
        </Typography>
        <Select
          value={alertThreshold}
          onChange={(event) => setAlertThreshold(String(event.target.value))}
          // use String() to prevent undefined from setting alertimpact
          sx={{ marginRight: "10px", minWidth: "800px" }}
          size="small"
        >
          {sortedSSVCPriorities.map((x) => (
            <MenuItem key={x} value={x}>
              {ssvcPriorityProps[x].displayName}
            </MenuItem>
          ))}
        </Select>
      </Box>
      <Box mb={2}>
        <Typography sx={{ fontWeight: 400 }} mb={1}>
          Email Address
        </Typography>
        <Box display="flex" alignItems="center">
          <FormControl
            sx={{ marginRight: "10px", minWidth: "715px" }}
            variant="outlined"
            size="small"
          >
            <OutlinedInput
              id="pteam-mail-address-field"
              type="text"
              autoComplete="new-password" // to avoid autocomplete by browser
              value={mailAddress}
              onChange={(event) => setMailAddress(event.target.value)}
            />
          </FormControl>
          <CheckButton onHandleClick={handleCheckMail} isLoading={checkEmail} />
        </Box>
        <Box mt={1}>{emailMessage}</Box>
      </Box>
      <Box mb={2}>
        <Typography sx={{ fontWeight: 400 }} mb={1}>
          Slack Incoming Webhook URL
        </Typography>
        <Box display="flex" alignItems="center">
          <FormControl
            sx={{ marginRight: "10px", minWidth: "715px" }}
            variant="outlined"
            size="small"
          >
            <OutlinedInput
              id="pteam-slack-url-field"
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

      <Box mb={4}>
        <Typography sx={{ fontWeight: 400 }}>Send by</Typography>
        <FormControlLabel
          control={
            <AndroidSwitch checked={slackEnable} onChange={() => setSlackEnable(!slackEnable)} />
          }
          labelPlacement="start"
          label="Slack"
        />
        <FormControlLabel
          control={
            <AndroidSwitch checked={mailEnable} onChange={() => setMailEnable(!mailEnable)} />
          }
          labelPlacement="start"
          label="Email"
        />
      </Box>
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
PTeamNotificationSetting.propTypes = {
  show: PropTypes.bool.isRequired,
};
