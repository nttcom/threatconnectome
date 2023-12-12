import { CheckCircleRounded as CheckCircleRoundedIcon } from "@mui/icons-material";
import {
  Box,
  Typography,
  Card,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import { green, grey } from "@mui/material/colors";
import { PropTypes } from "prop-types";
import React from "react";

export function AnalysisNoThreatsMsg(props) {
  const { ateam } = props;

  return (
    <>
      <Card
        variant="outlined"
        sx={{ border: `solid 3px ${green[700]}`, bgcolor: green[50], mb: "50px" }}
      >
        <Box display="flex" sx={{ margin: 4 }}>
          <Typography variant="h7">No threats found</Typography>
        </Box>
      </Card>
      <Box
        sx={{
          width: "50%",
          border: `solid ${grey[200]}`,
          borderRadius: "4px",
          marginBottom: "20px",
        }}
      >
        <Box
          sx={{ padding: "10px", backgroundColor: grey[100] }}
          display="flex"
          alignItems="center"
          justifyContent="space-between"
        >
          <Typography ml={1} fontWeight={700} variant="subtitle2">
            WATCHING LIST
          </Typography>
        </Box>
        <Divider />

        <List sx={{ padding: 0 }}>
          {ateam.pteams.map((pteam, index) => (
            <ListItem
              key={index}
              dense
              sx={{
                borderLeft: `solid 5px ${green[700]}`,
              }}
            >
              <ListItemIcon>
                <CheckCircleRoundedIcon color="success" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box display="flex" justifyContent="space-between">
                    <Typography display="flex">{pteam.pteam_name}</Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Box>
    </>
  );
}

AnalysisNoThreatsMsg.propTypes = {
  ateam: PropTypes.object.isRequired,
};
