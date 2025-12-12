import { Box, Button, Divider, TextField, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";

import { useViewportOffset } from "../hooks/useViewportOffset";
import { useUpdatePTeamMutation } from "../services/tcApi";
import {
  modalCommonButtonStyle,
  maxPTeamNameLengthInHalf,
  maxContactInfoLengthInHalf,
} from "../utils/const";
import { errorToString, countFullWidthAndHalfWidthCharacters } from "../utils/func";

export function PTeamGeneralSetting(props) {
  const { pteam } = props;

  const [pteamName, setPTeamName] = useState(pteam.pteam_name);
  const [contactInfo, setContactInfo] = useState(pteam.contact_info);

  const [updatePTeam] = useUpdatePTeamMutation();

  const { enqueueSnackbar } = useSnackbar();
  const viewportOffsetTop = useViewportOffset();

  const operationError = (error) =>
    enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" });

  const handlePTeamNameSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxPTeamNameLengthInHalf) {
      enqueueSnackbar(
        `Too long team name. Max length is ${maxPTeamNameLengthInHalf} in half-width or ${Math.floor(maxPTeamNameLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
          style: {
            marginTop: `${viewportOffsetTop}px`,
          },
        },
      );
    } else {
      setPTeamName(string);
    }
  };

  const handleContactInfoSetting = (string) => {
    if (countFullWidthAndHalfWidthCharacters(string.trim()) > maxContactInfoLengthInHalf) {
      enqueueSnackbar(
        `Too long contact info. Max length is ${maxContactInfoLengthInHalf} in half-width or ${Math.floor(maxContactInfoLengthInHalf / 2)} in full-width`,
        {
          variant: "error",
          style: {
            marginTop: `${viewportOffsetTop}px`,
          },
        },
      );
    } else {
      setContactInfo(string);
    }
  };

  const handleUpdatePTeam = async () => {
    const data = {
      pteam_name: pteamName,
      contact_info: contactInfo,
    };
    await updatePTeam({ path: { pteam_id: pteam.pteam_id }, body: data })
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
          Team name
        </Typography>
        <TextField
          size="small"
          value={pteamName}
          onChange={(event) => handlePTeamNameSetting(event.target.value)}
          variant="outlined"
          placeholder={`Max length is ${maxPTeamNameLengthInHalf} in half-width or ${Math.floor(maxPTeamNameLengthInHalf / 2)} in full-width`}
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
          onChange={(event) => handleContactInfoSetting(event.target.value)}
          variant="outlined"
          placeholder={`Max length is ${maxContactInfoLengthInHalf} in half-width or ${Math.floor(maxContactInfoLengthInHalf / 2)} in full-width`}
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
