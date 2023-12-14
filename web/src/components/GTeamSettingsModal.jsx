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

import { TabPanel } from "../components/TabPanel";
import { a11yProps } from "../utils/func.js";

import { GTeamAuthEditor } from "./GTeamAuthEditor";
import { GTeamGeneralSetting } from "./GTeamGeneralSetting";

export function GTeamSettingsModal(props) {
  const { setShow, show, defaultTabIndex } = props;
  const [tab, setTab] = useState(defaultTabIndex ?? 0);

  const handleClose = () => setShow(false);

  const handleChangeTab = (_, newTab) => setTab(newTab);

  return (
    <Dialog fullWidth onClose={handleClose} open={show} maxWidth="md">
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} variant="inherit" sx={{ fontWeight: 900 }}>
            GTeam settings
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
          </Tabs>
        </Box>
        <TabPanel index={0} value={tab}>
          <GTeamGeneralSetting show={show} />
        </TabPanel>
        <TabPanel index={1} value={tab}>
          <GTeamAuthEditor />
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
}
GTeamSettingsModal.propTypes = {
  setShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  defaultTabIndex: PropTypes.number,
};
