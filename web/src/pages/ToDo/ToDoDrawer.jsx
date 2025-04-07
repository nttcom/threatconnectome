import { Recommend as RecommendIcon, Warning as WarningIcon } from "@mui/icons-material";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import {
  Card,
  Chip,
  Drawer,
  FormControl,
  IconButton,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  Tooltip,
  Typography,
} from "@mui/material";
import Box from "@mui/material/Box";
import { green, yellow } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";

export function ToDoDrawer(props) {
  const { open, setOpen } = props;
  return (
    <Drawer anchor="right" open={open} onClose={() => setOpen(false)}>
      <Box>
        <Tooltip arrow title="Close">
          <IconButton size="large">
            <KeyboardDoubleArrowRightIcon fontSize="inherit" />
          </IconButton>
        </Tooltip>
      </Box>
      <Box sx={{ width: 800, px: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ pb: 1, fontWeight: "bold" }}>
            Ticket #XXXXXX
          </Typography>
        </Box>
        <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
          <Tabs value={1}>
            <Tab label="Ticket" value={1} />
            <Tab label="Topic" value={2} />
          </Tabs>
        </Box>
        {/* ticket */}
        <Stack spacing={2} sx={{ px: 2 }}>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              SSVC
            </Typography>
            <Chip label="Immediate" color="error" />
          </Box>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              CVE-ID
            </Typography>
            <Typography>CVE-XXXX-XXXX</Typography>
            <IconButton size="small">
              <OpenInNewIcon color="primary" fontSize="small" />
            </IconButton>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              Team
            </Typography>
            <Typography>team_name</Typography>
            <IconButton size="small">
              <OpenInNewIcon color="primary" fontSize="small" />
            </IconButton>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              Service
            </Typography>
            <Typography>Django</Typography>
            <IconButton size="small">
              <OpenInNewIcon color="primary" fontSize="small" />
            </IconButton>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              Artifact
            </Typography>
            <Typography>setuptools:pypi:python-pkg</Typography>
            <IconButton size="small">
              <OpenInNewIcon color="primary" fontSize="small" />
            </IconButton>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              Target
            </Typography>
            <Typography>Python</Typography>
          </Box>
          <Box sx={{ display: "flex" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              Safety Impact
            </Typography>
            <FormControl sx={{ width: 130 }} size="small" variant="standard">
              <Select defaultValue="test">
                <MenuItem value="test">Negligible</MenuItem>
                <MenuItem value="test2">test2</MenuItem>
                <MenuItem value="test3">test3</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ display: "flex" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              Status
            </Typography>
            <FormControl sx={{ width: 130 }} size="small" variant="standard">
              <Select defaultValue="test">
                <MenuItem value="test">Alerted</MenuItem>
                <MenuItem value="test2">test2</MenuItem>
                <MenuItem value="test3">test3</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ display: "flex" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              Due date
            </Typography>
          </Box>
          <Box sx={{ display: "flex" }}>
            <Typography variant="h6" sx={{ width: 170 }}>
              Assignees
            </Typography>
            <FormControl sx={{ width: 200 }} size="small" variant="standard">
              <Select defaultValue="test">
                <MenuItem value="test">sample@example.com</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Stack>
        {/* topic */}
        <Stack sx={{ px: 2 }} spacing={1}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              Artifact Tag
            </Typography>
            <Card variant="outlined" display="flex" sx={{ padding: 2 }}>
              <Typography variant="h5">setuptools:pypi:</Typography>
              <Box
                display="flex"
                flexDirection="row"
                justifyContent="center"
                sx={{ alignItems: "center" }}
              >
                <Box
                  alignItems="flexStart"
                  display="flex"
                  flexDirection="column"
                  sx={{ width: "50%", minWidth: "50%" }}
                >
                  <Box alignItems="center" display="flex" flexDirection="row" sx={{ ml: 2 }}>
                    <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
                  </Box>
                </Box>
                <Box
                  alignItems="center"
                  display="flex"
                  flexDirection="row"
                  sx={{ width: "50%", ml: 2 }}
                >
                  <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
                  <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                    -
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              Mitigations
            </Typography>
            <Card variant="outlined">
              <List>
                <ListItem>
                  <ListItemText primary="Update setuptools from version ['<70.0.0'] to ['70.0.0']" />
                </ListItem>
              </List>
            </Card>
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              Topic Tags
            </Typography>
            <List>
              <ListItem>
                <ListItemText primary={"-"} />
              </ListItem>
            </List>
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              Detail
            </Typography>
            <Card variant="outlined" sx={{ p: 2 }}>
              <Typography variant="body1">
                A vulnerability in the package_index module of pypa/setuptools versions up to 69.1.1
                allows for remote code execution via its download functions. These functions, which
                are used to download packages from URLs provided by users or retrieved from package
                index servers, are susceptible to code injection. If these functions are exposed to
                user-controlled inputs, such as package URLs, they can execute arbitrary commands on
                the system. The issue is fixed in version 70.0.
              </Typography>
            </Card>
          </Box>
        </Stack>
      </Box>
    </Drawer>
  );
}

ToDoDrawer.propTypes = {
  open: PropTypes.bool.required,
  setOpen: PropTypes.func.required,
};
