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
import { useTranslation } from "react-i18next";

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
import { errorToString, countFullWidthAndHalfWidthCharacters } from "../utils/func";
import { getSsvcPriorityProps, sortedSSVCPriorities } from "../utils/ssvcUtils";

import { CheckButton } from "./CheckButton";

export function PTeamNotificationSetting(props) {
  const { pteam } = props;
  const { t } = useTranslation("components", { keyPrefix: "PTeamNotificationSetting" });

  const [editingSlackUrl, setEditingSlackUrl] = useState(false);
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
    enqueueSnackbar(t("operationFailed", { error: errorToString(error) }), { variant: "error" });

  const handleMailAddressSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxEmailAddressLengthInHalf) {
      enqueueSnackbar(
        t("emailTooLong", {
          maxHalf: maxEmailAddressLengthInHalf,
          maxFull: Math.floor(maxEmailAddressLengthInHalf / 2),
        }),
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
        t("slackUrlTooLong", {
          maxHalf: maxSlackWebhookUrlLengthInHalf,
          maxFull: Math.floor(maxSlackWebhookUrlLengthInHalf / 2),
        }),
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
        <Typography>{t("connectionSuccess")}</Typography>
      </Box>
    );
  };

  const connectFailMessage = (error) => {
    return (
      <Box display="flex" sx={{ color: "error.main" }}>
        <ErrorOutlineIcon />
        <Typography>{t("connectionFailed", { error: errorToString(error) })}</Typography>
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
        enqueueSnackbar(t("updateSucceeded"), { variant: "success" });
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
          {t("alertThreshold")}
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
              {getSsvcPriorityProps()[ssvcPriority].displayName}
            </MenuItem>
          ))}
        </Select>
      </Box>
      <Box mb={2}>
        <Typography sx={{ fontWeight: 400 }} mb={1}>
          {t("emailAddress")}
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
              placeholder={t("emailPlaceholder", {
                maxHalf: maxEmailAddressLengthInHalf,
                maxFull: Math.floor(maxEmailAddressLengthInHalf / 2),
              })}
            />
          </FormControl>
          <CheckButton onHandleClick={handleCheckMail} isLoading={checkEmail} />
        </Box>
        <Box mt={1}>{emailMessage}</Box>
      </Box>
      <Box mb={2}>
        <Typography sx={{ fontWeight: 400 }} mb={1}>
          {t("slackWebhook")}
        </Typography>
        <Box display="flex" alignItems="center">
          <FormControl
            sx={{ marginRight: "10px", minWidth: "715px" }}
            variant="outlined"
            size="small"
          >
            <OutlinedInput
              id="pteam-slack-url-field"
              type={editingSlackUrl ? "text" : "password"}
              autoComplete="new-password" // to avoid autocomplete by browser
              value={slackUrl}
              onChange={(event) => handleSlackUrlSetting(event.target.value)}
              placeholder={t("slackPlaceholder", {
                maxHalf: maxSlackWebhookUrlLengthInHalf,
                maxFull: Math.floor(maxSlackWebhookUrlLengthInHalf / 2),
              })}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={() => setEditingSlackUrl(!editingSlackUrl)}
                    edge="end"
                  >
                    {editingSlackUrl ? <VisibilityOffIcon /> : <VisibilityIcon />}
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
        <Typography sx={{ fontWeight: 400 }}>{t("sendBy")}</Typography>
        <FormControlLabel
          control={
            <AndroidSwitch checked={slackEnable} onChange={() => setSlackEnable(!slackEnable)} />
          }
          labelPlacement="start"
          label={t("slack")}
        />
        <FormControlLabel
          control={
            <AndroidSwitch checked={mailEnable} onChange={() => setMailEnable(!mailEnable)} />
          }
          labelPlacement="start"
          label={t("email")}
        />
      </Box>
      <Divider />
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <Button onClick={() => handleUpdatePTeam()} sx={{ ...modalCommonButtonStyle, ml: 1 }}>
          {t("save")}
        </Button>
      </Box>
    </Box>
  );
}
PTeamNotificationSetting.propTypes = {
  pteam: PropTypes.object.isRequired,
};
