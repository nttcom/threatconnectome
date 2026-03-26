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
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { TabPanel } from "../components/TabPanel";
import dialogStyle from "../cssModule/dialog.module.css";
import { useSkipUntilAuthUserIsReady } from "../hooks/auth";
import { useGetPTeamQuery } from "../services/tcApi";
import { APIError } from "../utils/APIError";
import { a11yProps, errorToString } from "../utils/func";

import { PTeamGeneralSetting } from "./PTeamGeneralSetting";
import { PTeamNotificationSetting } from "./PTeamNotificationSetting";

export function PTeamSettingsModal(props) {
  const { pteamId, onSetShow, show, defaultTabIndex } = props;
  const { t } = useTranslation("components", { keyPrefix: "PTeamSettingsModal" });
  const [tab, setTab] = useState(defaultTabIndex ?? 0);

  const skip = useSkipUntilAuthUserIsReady() || !pteamId;

  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery({ path: { pteam_id: pteamId } }, { skip });

  if (skip) return <></>;
  if (pteamError)
    throw new APIError(errorToString(pteamError), {
      api: "getPTeam",
    });
  if (pteamIsLoading) return <>{t("loadingTeam")}</>;

  const handleClose = () => onSetShow(false);

  const handleChangeTab = (_, newTab) => setTab(newTab);

  return (
    <Dialog open={show} onClose={handleClose} fullWidth maxWidth="sm">
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          <Typography flexGrow={1} className={dialogStyle.dialog_title}>
            {t("title")}
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent sx={{ px: 2 }}>
        <Box
          borderBottom={1}
          borderBottomColor="divider"
          position="sticky"
          top={0}
          bgcolor="background.paper"
          zIndex={1}
        >
          <Tabs aria-label="tabs" onChange={handleChangeTab} value={tab}>
            <Tab label={t("tabGeneral")} {...a11yProps(0)} />
            <Tab label={t("tabNotification")} {...a11yProps(1)} />
          </Tabs>
        </Box>
        <TabPanel index={0} value={tab} mx={1}>
          <PTeamGeneralSetting pteam={pteam} />
        </TabPanel>
        <TabPanel index={1} value={tab} mx={1}>
          <PTeamNotificationSetting pteam={pteam} />
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
}
PTeamSettingsModal.propTypes = {
  pteamId: PropTypes.string.isRequired,
  onSetShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  defaultTabIndex: PropTypes.number,
};
