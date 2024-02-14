import {
  ArrowDropDown as ArrowDropDownIcon,
  CalendarMonth as CalendarMonthIcon,
  Check as CheckIcon,
  Clear as ClearIcon,
  Groups as GroupsIcon,
  Search as SearchIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Divider,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  MenuList,
  Pagination,
  Select,
  TextField,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { format } from "date-fns";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import { ATeamLabel } from "../components/ATeamLabel";
import { ATeamTopicMenu } from "../components/ATeamTopicMenu";
import { AnalysisNoThreatsMsg } from "../components/AnalysisNoThreatsMsg";
import { AnalysisTopic } from "../components/AnalysisTopic";
import { getATeam, getATeamAuth } from "../slices/ateam";
import { getATeamTopics } from "../utils/api";
import { difficulty, difficultyColors, noATeamMessage } from "../utils/const";
import { calcTimestampDiff, errorToString, utcStringToLocalDate } from "../utils/func";

export function Analysis() {
  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);

  const user = useSelector((state) => state.user.user);
  const ateam = useSelector((state) => state.ateam.ateam);
  const authorities = useSelector((state) => state.ateam.authorities);

  const perPageItems = [10, 20, 50, 100];
  const sortKeyItems = [
    { queryName: "threat_impact", dispName: "Threat impact" },
    { queryName: "threat_impact_desc", dispName: "Threat impact (desc)" },
    { queryName: "updated_at", dispName: "Updated date" },
    { queryName: "updated_at_desc", dispName: "Updated date (desc)" },
  ];

  /* controllable query params -- fix for api validation */
  let tmp;
  const [page, setPage] = useState((tmp = parseInt(params.get("page"))) > 0 ? tmp : 1);
  const [perPage, setPerPage] = useState(
    !((tmp = parseInt(params.get("perPage"))) > 0) // tmp <= 0 or NaN
      ? perPageItems[0]
      : tmp > 100
        ? perPageItems.slice(-1)[0]
        : tmp,
  );
  const [sortKey, setSortKey] = useState(
    sortKeyItems.map((item) => item.queryName).includes((tmp = params.get("sortKey")))
      ? tmp
      : sortKeyItems[0].queryName,
  );
  const [search, setSearch] = useState(params.get("search") || "");
  const [actualSearch, setActualSearch] = useState(params.get("search") || "");

  /* other controllables */
  const [pageInfo, setPageInfo] = useState();
  const [targetTopic, setTargetTopic] = useState();
  const [anchorEl, setAnchorEl] = useState();

  const ateamId = params.get("ateamId");

  useEffect(() => {
    /* Note: state.ateam.* are re-initialized when ateamId is changed. */
    if (!user.user_id || !ateamId || !ateam) return;
    async function fetchPageInfo() {
      const queryParams = {
        offset: perPage * (page - 1),
        limit: perPage,
        sort_key: sortKey,
        search: actualSearch,
      };
      await getATeamTopics(ateamId, queryParams)
        .then((response) => {
          const data = response.data;
          setPageInfo(data);
          setTargetTopic(data.topic_statuses?.length > 0 ? data.topic_statuses[0] : null);
        })
        .catch((error) => {
          setPageInfo(undefined);
          enqueueSnackbar(`Getting topics failed: ${errorToString(error)}`, {
            variant: "error",
          });
        });
    }

    /* Note:
     *   Calling setPage() or other setXXX is enough to re-call fetchPageInfo(), but
     *   it does not update actual query params. call navigate() to fix query params.
     */

    fetchPageInfo();
  }, [user, ateamId, ateam, page, perPage, sortKey, actualSearch, enqueueSnackbar]);

  useEffect(() => {
    if (!user.user_id || !ateamId) return;
    if (!ateam) dispatch(getATeam(ateamId));
  }, [dispatch, ateam, user, ateamId]);

  useEffect(() => {
    if (!user.user_id || !ateamId || !ateam) return;
    if (!authorities) dispatch(getATeamAuth(ateamId));
  }, [dispatch, ateamId, ateam, authorities, user]);

  if (!ateamId) return <>{noATeamMessage}</>;
  if (!user.user_id || !ateam || !authorities || !pageInfo) return <>Now loading...</>;

  const handleMenuClick = (event) => setAnchorEl(event.currentTarget);

  const handleMenuClose = () => setAnchorEl(null);

  const changeSortKey = (sortTarget) => {
    setSortKey(sortTarget);
    params.set("sortKey", sortTarget);
    handleMenuClose();
    navigate(location.pathname + "?" + params.toString());
  };

  const applySearch = (targetSearch) => {
    setSearch(targetSearch);
    setActualSearch(targetSearch);
    params.set("search", targetSearch);
    navigate(location.pathname + "?" + params.toString());
  };

  const isAdmin = (authorities.find((x) => x.user_id === user.user_id)?.authorities ?? []).includes(
    "admin",
  );
  const pageMax = Math.ceil(pageInfo.num_topics / perPage);
  if (page > pageMax && pageMax > 0) setPage(pageMax);

  if (ateam.pteams.length === 0) {
    return (
      <>
        <ATeamLabel ateam={ateam} />
        <>No watching teams.</>
        <ATeamTopicMenu />
      </>
    );
  }
  if (!actualSearch.length > 0 && !pageInfo?.num_topics > 0) {
    return (
      <>
        <ATeamLabel ateam={ateam} />
        <ATeamTopicMenu />
        <AnalysisNoThreatsMsg ateam={ateam} />
      </>
    );
  }
  return (
    <>
      <ATeamLabel ateam={ateam} />
      <Box display="flex" alignItems="center" sx={{ mt: -1 }}>
        {/* Pagination */}
        <Pagination
          shape="rounded"
          page={page}
          count={pageMax}
          onChange={(event, value) => {
            setPage(value);
            params.set("page", value);
            navigate(location.pathname + "?" + params.toString());
          }}
        />
        {/* perPage selector */}
        <Select
          size="small"
          variant="standard"
          value={perPage}
          onChange={(event) => {
            setPerPage(event.target.value);
            setPage(1);
            params.set("perPage", event.target.value);
            params.set("page", 1);
            navigate(location.pathname + "?" + params.toString());
          }}
        >
          {perPageItems.map((num) => (
            <MenuItem key={num} value={num} sx={{ justifyContent: "flex-end" }}>
              <Typography variant="body2" sx={{ mt: 0.3 }}>
                {num} Rows
              </Typography>
            </MenuItem>
          ))}
        </Select>
        <Box flexGrow={1} />
        <ATeamTopicMenu />
      </Box>
      <Box
        display="flex"
        sx={{ border: `solid ${grey[200]}`, borderRadius: "4px", marginBottom: "25px" }}
      >
        {/* Topic list */}
        <Box
          sx={{ width: "35%", minHeight: "700px", borderRight: `solid ${grey[200]}` }}
          display="flex"
          flexDirection="column"
        >
          {/* Search topics */}
          <Box sx={{ padding: "10px" }} display="flex" justifyContent="center">
            <TextField
              sx={{ minWidth: "360px" }}
              placeholder="Search topics"
              label={search === actualSearch ? "" : "(press ENTER to apply)"}
              size="small"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") applySearch(event.target.value);
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => applySearch("")} size="small">
                      <ClearIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
          <Divider />
          {/* Total topic and sort */}
          <Box
            sx={{ padding: "10px", backgroundColor: grey[100] }}
            display="flex"
            alignItems="center"
            justifyContent="space-between"
          >
            <Typography ml={1} fontWeight={900} variant="subtitle2">
              {pageInfo.num_topics} topics
            </Typography>
            <Button
              id="basic-button"
              aria-controls={anchorEl ? "basic-menu" : undefined}
              aria-haspopup="true"
              aria-expanded={anchorEl ? "true" : undefined}
              onClick={handleMenuClick}
              endIcon={<ArrowDropDownIcon />}
              sx={{
                textTransform: "none",
                color: grey[800],
                "&:hover": {
                  backgroundColor: grey[200],
                  color: grey[900],
                },
              }}
            >
              Sort
            </Button>
            <Menu
              id="basic-menu"
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              MenuListProps={{
                "aria-labelledby": "basic-button",
              }}
            >
              <MenuList dense>
                {sortKeyItems.map((item) => {
                  const selected = sortKey === item.queryName;
                  return (
                    <MenuItem key={item.queryName} onClick={() => changeSortKey(item.queryName)}>
                      <ListItemIcon>{selected && <CheckIcon />}</ListItemIcon>
                      <Typography fontWeight={selected && 900}>{item.dispName}</Typography>
                    </MenuItem>
                  );
                })}
              </MenuList>
            </Menu>
          </Box>
          <Divider />
          {/* Topics */}
          <List sx={{ padding: 0 }} id="topicListElem">
            {pageInfo.topic_statuses.map((topic, index) => (
              <ListItem
                key={index}
                dense
                disablePadding
                divider={true}
                sx={{
                  borderLeft: `solid 5px ${difficultyColors[difficulty[topic.threat_impact - 1]]}`,
                }}
              >
                <ListItemButton
                  onClick={() => setTargetTopic(topic)}
                  selected={topic.topic_id === targetTopic?.topic_id}
                >
                  <ListItemText
                    primary={
                      <Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography fontWeight={900}>{topic.title}</Typography>
                          <Box display="flex" sx={{ color: grey[600] }}>
                            <GroupsIcon />
                            <Typography ml={1} fontWeight={900}>
                              {topic.pteams.length}
                            </Typography>
                          </Box>
                        </Box>
                        <Box display="flex" justifyContent="space-between">
                          <Typography mt={1} mr={1} variant="caption">
                            {`Updated ${calcTimestampDiff(topic.updated_at)}`}
                          </Typography>
                          {topic.pteams[0].statuses[0].topic_status === "scheduled" && (
                            <Box display="flex" alignItems="flex-end">
                              <CalendarMonthIcon fontSize="small" sx={{ color: grey[700] }} />
                              <Typography ml={0.5} variant="caption">
                                {format(
                                  utcStringToLocalDate(topic.pteams[0].statuses[0].scheduled_at),
                                  "yyyy/MM/dd",
                                )}
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </Box>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
        {/* Topic detail */}
        {targetTopic && (
          <Box sx={{ width: "65%" }}>
            <AnalysisTopic user={user} ateam={ateam} targetTopic={targetTopic} isAdmin={isAdmin} />
          </Box>
        )}
      </Box>
      <Box display="flex" alignItems="center" sx={{ mt: -1, mb: 5 }}>
        {/* Pagination */}
        <Pagination
          shape="rounded"
          page={page}
          count={pageMax}
          onChange={(event, value) => {
            setPage(value);
            params.set("page", value);
            navigate(location.pathname + "?" + params.toString());
          }}
        />
        {/* perPage selector */}
        <Select
          size="small"
          variant="standard"
          value={perPage}
          onChange={(event) => {
            setPerPage(event.target.value);
            setPage(1);
            params.set("perPage", event.target.value);
            params.set("page", 1);
            navigate(location.pathname + "?" + params.toString());
          }}
        >
          {perPageItems.map((num) => (
            <MenuItem key={num} value={num} sx={{ justifyContent: "flex-end" }}>
              <Typography variant="body2" sx={{ mt: 0.3 }}>
                {num} Rows
              </Typography>
            </MenuItem>
          ))}
        </Select>
        <Box flexGrow={1} />
      </Box>
    </>
  );
}
