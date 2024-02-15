import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { TabPanel } from "../components/TabPanel";
import { getPTeamGroups, getPTeamTagsSummary } from "../slices/pteam";
import { a11yProps } from "../utils/func.js";

import { PTeamAuthEditor } from "./PTeamAuthEditor";
import { PTeamAutoClose } from "./PTeamAutoClose";
import { PTeamGeneralSetting } from "./PTeamGeneralSetting";
import { SBOMDropArea } from "./SBOMDropArea";

export function PTeamSettingsModal(props) {
  const dispatch = useDispatch();

  const { onSetShow, show, defaultTabIndex } = props;
  const [tab, setTab] = useState(defaultTabIndex ?? 0);

  const handleClose = () => onSetShow(false);

  const handleChangeTab = (_, newTab) => setTab(newTab);

  const pteamId = useSelector((state) => state.pteam.pteamId); // dispatched by App or PTeamSelector

  const handleSBOMUploaded = () => {
    dispatch(getPTeamTagsSummary(pteamId));
    dispatch(getPTeamGroups(pteamId));
  };

  return (
    <Dialog fullWidth onClose={handleClose} open={show} maxWidth="md">
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} variant="inherit" sx={{ fontWeight: 900 }}>
            PTeam settings
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box borderBottom={1} borderBottomColor="divider">
          <Tabs aria-label="tabs" onChange={handleChangeTab} value={tab}>
            <Tab label="General" {...a11yProps(0)} />
            <Tab label="Authorities" {...a11yProps(1)} />
            <Tab label="Upload" {...a11yProps(2)} />
            <Tab label="Auto Close" {...a11yProps(3)} />
          </Tabs>
        </Box>
        <TabPanel index={0} value={tab}>
          <PTeamGeneralSetting show={show} />
        </TabPanel>
        <TabPanel index={1} value={tab}>
          <PTeamAuthEditor />
        </TabPanel>
        <TabPanel index={2} value={tab}>
          <SBOMDropArea pteamId={pteamId} onUploaded={handleSBOMUploaded} />
        </TabPanel>
        <TabPanel index={3} value={tab}>
          <PTeamAutoClose />
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
}
PTeamSettingsModal.propTypes = {
  onSetShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  defaultTabIndex: PropTypes.number,
};
