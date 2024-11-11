import SearchIcon from "@mui/icons-material/Search";
import SortIcon from "@mui/icons-material/Sort";
import {
  Box,
  Button,
  Card,
  CardHeader,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  List,
  ListItem,
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
  const isDone = false;
  const remainingTime = 70;
  const remainingTimeColor =
    remainingTime === 0 ? "error" : remainingTime < 20 ? "warning" : "primary";

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
                      <ListItem
                        sx={{
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "flex-start",
                        }}
                      >
                        <ListItemText
                          primary={
                            <Typography
                              variant="subtitle2"
                              sx={{
                                fontWeight: "bold",
                                overflow: "hidden",
                                maxHeight: 44,
                              }}
                            >
                              CVE-XXXX-XXXXX
                            </Typography>
                          }
                          secondary={
                            <>
                              <Typography variant="caption" noWrap>
                                Team: team_name
                              </Typography>
                              <br />
                              <Typography variant="caption" noWrap>
                                Service: service_name
                              </Typography>
                              {item.title === "Immediate" &&
                                (isDone ? (
                                  <>
                                    <br />
                                    <Typography variant="caption" noWrap>
                                      Status: scheduled
                                    </Typography>
                                    <br />
                                    <Typography variant="caption" noWrap>
                                      Assignees: test@example.com
                                    </Typography>
                                  </>
                                ) : (
                                  <>
                                    <Button
                                      variant="contained"
                                      size="small"
                                      startIcon={<SearchIcon />}
                                      sx={{ my: 1 }}
                                      color={remainingTimeColor}
                                    >
                                      Investigate
                                    </Button>
                                    <Box sx={{ position: "relative", height: 120 }}>
                                      <CircularProgress
                                        size="120px"
                                        variant="determinate"
                                        value={100}
                                        sx={{ color: "#e6e6e6", position: "absolute" }}
                                      />
                                      <Box sx={{ position: "absolute" }}>
                                        <Box sx={{ position: "relative", display: "inline-flex" }}>
                                          <CircularProgress
                                            size="120px"
                                            variant="determinate"
                                            value={remainingTime}
                                            color={remainingTimeColor}
                                          />
                                          <Box
                                            sx={{
                                              top: 0,
                                              left: 0,
                                              bottom: 0,
                                              right: 0,
                                              position: "absolute",
                                              display: "flex",
                                              alignItems: "center",
                                              justifyContent: "center",
                                            }}
                                          >
                                            <Typography
                                              variant="caption"
                                              component="div"
                                              color="text.secondary"
                                              sx={{ fontSize: 30, fontWeight: "bold" }}
                                            >
                                              10:00
                                            </Typography>
                                          </Box>
                                        </Box>
                                      </Box>
                                    </Box>
                                  </>
                                ))}
                            </>
                          }
                        />
                      </ListItem>
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
