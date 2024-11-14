import { Box, Button, TextField, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useUpdateATeamMutation, useGetATeamQuery } from "../services/tcApi";
import { modalCommonButtonStyle } from "../utils/const";
import { errorToString } from "../utils/func";

export function ATeamGeneralSetting(props) {
  const { ateamId, show } = props;
  const [ateamName, setATeamName] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [slackUrl, setSlackUrl] = useState("");

  const { enqueueSnackbar } = useSnackbar();
  const [updateATeam] = useUpdateATeamMutation();

  const skip = useSkipUntilAuthTokenIsReady();

  const {
    data: ateam,
    error: ateamError,
    isLoading: ateamIsLoading,
  } = useGetATeamQuery(ateamId, { skip });

  useEffect(() => {
    if (ateam) {
      setATeamName(ateam.ateam_name);
      setContactInfo(ateam.contact_info);
      setSlackUrl(ateam.alert_slack.webhook_url);
    }
  }, [show, ateam]);

  if (skip) return <></>;
  if (ateamError) return <>{`Cannot get Ateam: ${errorToString(ateamError)}`}</>;
  if (ateamIsLoading) return <>Now loading Ateam...</>;

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
  ateamId: PropTypes.string.isRequired,
  show: PropTypes.bool.isRequired,
};
