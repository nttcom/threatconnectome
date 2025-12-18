import {
  Box,
  Card,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Typography,
} from "@mui/material";

import { ActionTypeIcon } from "./ActionTypeIcon";

export default {
  title: "Components/ActionTypeIcon",
  component: ActionTypeIcon,
};

// ActionTypeIcon
export const Default = {};

// VulnerabilityView style: Example usage within a ListItem
export const InListItem = {
  render: () => (
    <Card variant="outlined" sx={{ m: 1, p: 2, maxWidth: 500 }}>
      <Typography variant="h6" sx={{ fontWeight: "bold", mb: 1 }}>
        Update
      </Typography>
      <List>
        <ListItem>
          <ListItemIcon>
            <ActionTypeIcon />
          </ListItemIcon>
          <ListItemText primary="Update lodash from [4.17.0] to [4.17.21]" />
        </ListItem>
      </List>
    </Card>
  ),
};

// VulnDetailView style: Example usage within a MenuItem
export const InMenuItem = {
  render: () => (
    <Card variant="outlined" sx={{ m: 1, p: 2, maxWidth: 500 }}>
      <Typography sx={{ fontWeight: "bold", mb: 1 }}>Update</Typography>
      <Box>
        <MenuItem
          sx={{
            alignItems: "center",
            display: "flex",
            flexDirection: "row",
          }}
        >
          <ActionTypeIcon />
          <Box display="flex" flexDirection="column">
            <Typography noWrap variant="body">
              Update express from [4.0.0] to [4.18.2]
            </Typography>
          </Box>
        </MenuItem>
        <MenuItem
          sx={{
            alignItems: "center",
            display: "flex",
            flexDirection: "row",
          }}
        >
          <ActionTypeIcon />
          <Box display="flex" flexDirection="column">
            <Typography noWrap variant="body">
              Update axios from [0.21.0] to [0.21.4]
            </Typography>
          </Box>
        </MenuItem>
      </Box>
    </Card>
  ),
};

// ReportCompletedActions style: Selectable MenuItem example
export const InSelectableMenuItem = {
  render: () => (
    <Card variant="outlined" sx={{ m: 1, p: 2, maxWidth: 500 }}>
      <Typography sx={{ fontWeight: "bold", mb: 1 }}>
        Select the actions you have completed
      </Typography>
      <MenuItem
        selected={true}
        sx={{
          alignItems: "center",
          display: "flex",
          flexDirection: "row",
        }}
      >
        <ActionTypeIcon />
        <Box display="flex" flexDirection="column">
          <Typography noWrap variant="body" width={400}>
            Update lodash from [4.17.0, 4.17.19] to [4.17.21]
          </Typography>
        </Box>
      </MenuItem>
    </Card>
  ),
};
