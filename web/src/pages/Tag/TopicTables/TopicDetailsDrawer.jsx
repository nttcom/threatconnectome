import { Recommend as RecommendIcon, Warning as WarningIcon } from "@mui/icons-material";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import OpenInFullIcon from "@mui/icons-material/OpenInFull";
import {
  Box,
  Card,
  Chip,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import { green, yellow } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";
import { Link } from "react-router-dom";

export function TopicDetailsDrawer(props) {
  const { open, setOpen } = props;

  return (
    <Drawer anchor="right" open={open} onClose={() => setOpen(false)}>
      <Box>
        <Tooltip arrow title="Close">
          <IconButton size="large" onClick={() => setOpen(false)}>
            <KeyboardDoubleArrowRightIcon fontSize="inherit" />
          </IconButton>
        </Tooltip>
        <Link to="/vulnerability" preventScrollReset={true}>
          <Tooltip title="Open in full page">
            <IconButton size="large">
              <OpenInFullIcon />
            </IconButton>
          </Tooltip>
        </Link>
      </Box>
      <Box sx={{ width: 800, px: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: "bold", py: 2 }}>
          urllib3: proxy-authorization request header is not stripped during cross-origin redirects
        </Typography>
        <Stack spacing={2}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              Artifact Tag
            </Typography>
            <Card variant="outlined" sx={{ p: 2 }}>
              <Typography variant="h5">urllib3:pypi:pipenv</Typography>
              <Box display="flex" flexDirection="row" justifyContent="center">
                {/* left half -- affected versions */}
                <Box
                  alignItems="flexStart"
                  display="flex"
                  flexDirection="column"
                  sx={{ width: "50%", minWidth: "50%" }}
                >
                  <Box alignItems="center" display="flex" flexDirection="row" sx={{ ml: 2 }}>
                    <WarningIcon sx={{ fontSize: 32, color: yellow[900] }} />
                    <Tooltip title="<0.38.1" placement="right">
                      <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                        {"<0.38.1"}
                      </Typography>
                    </Tooltip>
                  </Box>
                </Box>
                {/* right half -- patched versions */}
                <Box
                  alignItems="center"
                  display="flex"
                  flexDirection="row"
                  sx={{ width: "50%", ml: 2 }}
                >
                  <RecommendIcon sx={{ fontSize: 32, color: green[500] }} />
                  <Typography noWrap sx={{ fontSize: 32, mx: 2 }}>
                    {"-" /* not yet supported */}
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
                  <ListItemText primary="M1037: Filter Network Traffic" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="WAF: add rules XXXXXXXXCCCCC" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="WAF: add rules XXXXXXXXCCCCC" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="WAF: add rules XXXXXXXXCCCCC" />
                </ListItem>
              </List>
            </Card>
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              Topic tags
            </Typography>
            <Chip label="CVE-2024-37891" sx={{ m: 1 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              Detail
            </Typography>
            <Card variant="outlined" sx={{ p: 2 }}>
              <Typography variant="body1">
                Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor
                incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
                exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute
                irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
                pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
                deserunt mollit anim id est laborum.
              </Typography>
            </Card>
          </Box>
        </Stack>
      </Box>
    </Drawer>
  );
}

TopicDetailsDrawer.propTypes = {
  open: PropTypes.bool,
  setOpen: PropTypes.func,
};
