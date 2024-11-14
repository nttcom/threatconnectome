import { Box, Button, Divider, TextField, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { useUpdatePTeamMutation } from "../services/tcApi";
import { modalCommonButtonStyle } from "../utils/const";
import { errorToString } from "../utils/func";

export function PTeamGeneralSetting(props) {
  const { pteam } = props;

  const [pteamName, setPTeamName] = useState(pteam.pteam_name);
  const [contactInfo, setContactInfo] = useState(pteam.contact_info);

  const [updatePTeam] = useUpdatePTeamMutation();

  const { enqueueSnackbar } = useSnackbar();

  const operationError = (error) =>
    enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" });

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
  pteam: PropTypes.object.isRequired,
};
