import SortIcon from "@mui/icons-material/Sort";
import {
  Box,
  Card,
  CardHeader,
  Divider,
  Grid,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Typography,
} from "@mui/material";
import { amber, grey, orange, red } from "@mui/material/colors";
import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { ATeamLabel } from "../components/ATeamLabel";
import { getATeam } from "../slices/ateam";

export function SSVCPriority() {
  const SSVCPriorityList = [
    { title: "Immediate", color: red[600] },
    { title: "Out-of-Cycle", color: orange[600] },
    { title: "Scheduled", color: amber[600] },
    { title: "Defer", color: grey[600] },
  ];
  const ateam = useSelector((state) => state.ateam.ateam);
  const ateamId = useSelector((state) => state.ateam.ateamId);
  const dispatch = useDispatch();

  useEffect(() => {
    if (!ateam) dispatch(getATeam(ateamId));
  }, [dispatch, ateamId, ateam]);

  if (!ateam) return <></>;

  return (
    <Box
      sx={{
        height: "calc(100vh - 96px)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box sx={{ flex: 0 }}>
        <ATeamLabel ateam={ateam} />
      </Box>
      <Grid container spacing={1} sx={{ flex: 1 }}>
        {SSVCPriorityList.map((item) => (
          <Grid key={item.title} item xs={3} sx={{ height: "100%" }}>
            <Card sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
              <Box sx={{ flex: 0 }}>
                <CardHeader
                  title={item.title}
                  sx={{
                    backgroundColor: item.color,
                    color: "white",
                    textWrap: "nowrap",
                  }}
                />
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    px: 2,
                  }}
                >
                  <Typography
                    variant="subtitle1"
                    sx={{ color: "text.secondary", textWrap: "nowrap", overflow: "hidden" }}
                  >
                    999999 tickets
                  </Typography>
                  <IconButton>
                    <SortIcon />
                  </IconButton>
                </Box>
                <Divider />
              </Box>
              <Box
                sx={{
                  flexGrow: 1,
                  flexBasis: 0,
                  overflowY: "auto",
                }}
              >
                <List
                  sx={{
                    p: 0,
                  }}
                >
                  {[...Array(20)].map((_, i) => (
                    <React.Fragment key={i}>
                      <ListItemButton
                        sx={{
                          height: 152,
                        }}
                      >
                        <ListItemText
                          primary={
                            <Typography
                              variant="subtitle2"
                              sx={{
                                fontWeight: "bold",
                                display: "-webkit-box",
                                "-webkit-box-orient": "vertical",
                                "-webkit-line-clamp": "2",
                                overflow: "hidden",
                                maxHeight: 44,
                              }}
                            >
                              sqlparse: parsing heavily nested list leads to denial of service
                            </Typography>
                          }
                          secondary={
                            <>
                              <Typography component="div" variant="caption" noWrap>
                                Team: team_name
                              </Typography>
                              <Typography component="div" variant="caption" noWrap>
                                Status: Alerted
                              </Typography>
                              <Typography component="div" variant="caption" noWrap>
                                Service: service_name
                              </Typography>
                              <Typography component="div" variant="caption" noWrap>
                                Assignees: test@example.com
                              </Typography>
                            </>
                          }
                        />
                      </ListItemButton>
                      <Divider />
                    </React.Fragment>
                  ))}
                </List>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
