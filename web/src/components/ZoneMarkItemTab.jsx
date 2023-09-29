import { Business as BusinessIcon, Clear as ClearIcon } from "@mui/icons-material";
import {
  Box,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  IconButton,
  ListItemButton,
} from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import ActionTypeIcon from "../components/ActionTypeIcon";
import TabPanel from "../components/TabPanel";
import ThreatImpactStatusChip from "../components/ThreatImpactStatusChip";
import ZoneItemDeleteModal from "../components/ZoneItemDeleteModal";

function a11yProps(index) {
  return {
    id: `zone-item-tab-${index}`,
    "aria-controls": `zone-item-tabpanel-${index}`,
  };
}

export default function ZoneMarkItemTab(props) {
  const { zone } = props;
  const [value, setValue] = React.useState(0);
  const [itemDeleteOpen, setItemDeleteOpen] = useState(false);
  const [itemType, setItemType] = useState("");
  const [itemId, setItemId] = useState("");

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <>
      <Box sx={{ width: "100%" }}>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs value={value} onChange={handleChange} aria-label="zone item tabs" component="div">
            <Tab label="Topics" {...a11yProps(0)} />
            <Tab label="Actions" {...a11yProps(1)} />
            <Tab label="PTeams" {...a11yProps(2)} />
          </Tabs>
        </Box>
        <TabPanel value={value} index={0}>
          <List component="div" style={{ maxHeight: 300, overflow: "auto", border: "0px" }}>
            {zone.topics?.map((topic) => (
              <ListItem
                key={topic.topic_id}
                secondaryAction={
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={() => {
                      setItemType("topic");
                      setItemId(topic.topic_id);
                      setItemDeleteOpen(true);
                    }}
                  >
                    <ClearIcon />
                  </IconButton>
                }
              >
                <ListItemButton>
                  <Box sx={{ mr: "5px" }}>
                    <ThreatImpactStatusChip
                      threatImpact={topic.threat_impact ?? 4}
                      statusCounts={{ alerted: 0, scheduled: 0, acknowledged: 0, completed: 0 }}
                    />
                  </Box>
                  <ListItemText primary={topic.title} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </TabPanel>
        <TabPanel value={value} index={1}>
          <List component="div" style={{ maxHeight: 300, overflow: "auto", border: "0px" }}>
            {zone.actions?.map((action) => (
              <ListItem
                key={action.action_id}
                secondaryAction={
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={() => {
                      setItemType("action");
                      setItemId(action.action_id);
                      setItemDeleteOpen(true);
                    }}
                  >
                    <ClearIcon />
                  </IconButton>
                }
              >
                <ListItemButton>
                  <Box sx={{ mt: "5px", mr: "5px" }}>
                    <ActionTypeIcon
                      disabled={!action.recommended}
                      actionType={action.action_type}
                    />
                  </Box>
                  <ListItemText primary={action.action} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </TabPanel>
        <TabPanel value={value} index={2}>
          <List component="div" style={{ maxHeight: 300, overflow: "auto", border: "0px" }}>
            {zone.pteams?.map((pteam) => (
              <ListItem
                key={pteam.pteam_id}
                secondaryAction={
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={() => {
                      setItemType("PTeam");
                      setItemId(pteam.pteam_id);
                      setItemDeleteOpen(true);
                    }}
                  >
                    <ClearIcon />
                  </IconButton>
                }
              >
                <ListItemButton>
                  <Box sx={{ mt: "5px", mr: "5px" }}>
                    <BusinessIcon />
                  </Box>
                  <ListItemText primary={pteam.pteam_name} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </TabPanel>
      </Box>
      <ZoneItemDeleteModal
        setShow={setItemDeleteOpen}
        show={itemDeleteOpen}
        zone={zone}
        itemType={itemType}
        itemId={itemId}
      />
    </>
  );
}

ZoneMarkItemTab.propTypes = {
  zone: PropTypes.object.isRequired,
};
