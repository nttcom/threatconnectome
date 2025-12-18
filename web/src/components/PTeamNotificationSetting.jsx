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
import { useState } from "react";

import { useViewportOffset } from "../hooks/useViewportOffset";
import {
  useCheckMailMutation,
  useCheckSlackMutation,
  useUpdatePTeamMutation,
} from "../services/tcApi";
import {
  modalCommonButtonStyle,
  maxEmailAddressLengthInHalf,
  maxSlackWebhookUrlLengthInHalf,
} from "../utils/const";
import { ssvcPriorityProps, sortedSSVCPriorities } from "../utils/ssvcUtils";
import { errorToString, countFullWidthAndHalfWidthCharacters } from "../utils/func";

import { CheckButton } from "./CheckButton";

export function PTeamNotificationSetting(props) {
  const { pteam } = props;

  const [edittingSlackUrl, setEdittingSlackUrl] = useState(false);
  const [slackUrl, setSlackUrl] = useState(pteam.alert_slack.webhook_url);
  const [slackEnable, setSlackEnable] = useState(pteam.alert_slack.enable);
  const [mailAddress, setMailAddress] = useState(pteam.alert_mail.address);
  const [mailEnable, setMailEnable] = useState(pteam.alert_mail.enable);
  const [alertThreshold, setAlertThreshold] = useState(pteam.alert_ssvc_priority);
  const [checkSlack, setCheckSlack] = useState(false);
  const [checkEmail, setCheckEmail] = useState(false);
  const [slackMessage, setSlackMessage] = useState();
  const [emailMessage, setEmailMessage] = useState();

  const { enqueueSnackbar } = useSnackbar();
  const viewportOffsetTop = useViewportOffset();

  const [postCheckMail] = useCheckMailMutation();
  const [postCheckSlack] = useCheckSlackMutation();
  const [updatePTeam] = useUpdatePTeamMutation();

  const operationError = (error) =>
    enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" });

  const handleMailAddressSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxEmailAddressLengthInHalf) {
      enqueueSnackbar(
        `Too long email address. Max length is ${maxEmailAddressLengthInHalf} in half-width or ${Math.floor(maxEmailAddressLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
          style: {
            marginTop: `${viewportOffsetTop}px`,
          },
        },
      );
    } else {
      setMailAddress(string);
    }
  };

  const handleSlackUrlSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxSlackWebhookUrlLengthInHalf) {
      enqueueSnackbar(
        `Too long Slack webhook URL. Max length is ${maxSlackWebhookUrlLengthInHalf} in half-width or ${Math.floor(maxSlackWebhookUrlLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
          style: {
            marginTop: `${viewportOffsetTop}px`,
          },
        },
      );
    } else {
      setSlackUrl(string);
    }
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
        <Typography>Connection failed. Reason: {errorToString(error)}</Typography>
      </Box>
    );
  };

  const handleUpdatePTeam = async () => {
    const data = {
      alert_slack: { enable: slackEnable, webhook_url: slackUrl },
      alert_mail: { enable: mailEnable, address: mailAddress },
      alert_ssvc_priority: alertThreshold,
    };
    await updatePTeam({ path: { pteam_id: pteam.pteam_id }, body: data })
      .unwrap()
      .then(() => {
        enqueueSnackbar("update pteam info succeeded", { variant: "success" });
      })
      .catch((error) => operationError(error));
  };

  const handleCheckSlack = async () => {
    setCheckSlack(true);
    setSlackMessage();
    await postCheckSlack({ body: { slack_webhook_url: slackUrl } })
      .unwrap()
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
    await postCheckMail({ body: { email: mailAddress } })
      .unwrap()
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
          {sortedSSVCPriorities.map((ssvcPriority) => (
            <MenuItem key={ssvcPriority} value={ssvcPriority}>
              {ssvcPriorityProps[ssvcPriority].displayName}
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
              onChange={(event) => handleMailAddressSetting(event.target.value)}
              placeholder={`Max length is ${maxEmailAddressLengthInHalf} in half-width or ${Math.floor(maxEmailAddressLengthInHalf / 2)} in full-width`}
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
              onChange={(event) => handleSlackUrlSetting(event.target.value)}
              placeholder={`Max length is ${maxSlackWebhookUrlLengthInHalf} in half-width or ${Math.floor(maxSlackWebhookUrlLengthInHalf / 2)} in full-width`}
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
  pteam: PropTypes.object.isRequired,
};
