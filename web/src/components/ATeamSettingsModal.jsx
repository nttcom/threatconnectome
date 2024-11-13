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
import PropTypes from "prop-types";
import React, { useState } from "react";

import { TabPanel } from "../components/TabPanel";
import dialogStyle from "../cssModule/dialog.module.css";
import { a11yProps } from "../utils/func.js";

import { ATeamAuthEditor } from "./ATeamAuthEditor";
import { ATeamGeneralSetting } from "./ATeamGeneralSetting";
import { ATeamNotificationSetting } from "./ATeamNotificationSetting";

export function ATeamSettingsModal(props) {
  const { ateamId, onSetShow, show, defaultTabIndex } = props;
  const [tab, setTab] = useState(defaultTabIndex ?? 0);

  const handleClose = () => onSetShow(false);

  const handleChangeTab = (_, newTab) => setTab(newTab);

  return (
    <Dialog open={show} onClose={handleClose} fullWidth maxWidth="md">
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} className={dialogStyle.dialog_title}>
            ATeam settings
          </Typography>
          <IconButton onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box borderBottom={1} borderBottomColor="divider">
          <Tabs aria-label="tabs" onChange={handleChangeTab} value={tab}>
            <Tab label="General" {...a11yProps(0)} />
            <Tab label="Notification" {...a11yProps(1)} />
            <Tab label="Authorities" {...a11yProps(2)} />
          </Tabs>
        </Box>
        <TabPanel index={0} value={tab}>
          <ATeamGeneralSetting ateamId={ateamId} show={show} />
        </TabPanel>
        <TabPanel index={1} value={tab}>
          <ATeamNotificationSetting ateamId={ateamId} show={show} />
        </TabPanel>
        <TabPanel index={2} value={tab}>
          <ATeamAuthEditor ateamId={ateamId} />
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
}
ATeamSettingsModal.propTypes = {
  ateamId: PropTypes.string.isRequired,
  onSetShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  defaultTabIndex: PropTypes.number,
};
