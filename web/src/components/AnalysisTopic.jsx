import { Delete as DeleteIcon, Edit as EditIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  IconButton,
  Link,
  Paper,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import ActionItem from "../components/ActionItem";
import CommentDeleteModal from "../components/CommentDeleteModal";
import TabPanel from "../components/TabPanel";
import ThreatImpactChip from "../components/ThreatImpactChip";
import TopicModal from "../components/TopicModal";
import UUIDTypography from "../components/UUIDTypography";
import WarningTooltip from "../components/WarningTooltip";
import { getTopic } from "../slices/topics";
import {
  createATeamTopicComment as apiCreateATeamTopicComment,
  getATeamTopicComments as apiGetATeamTopicComments,
  getPTeamTag as apiGetPTeamTag,
  updateATeamTopicComment as apiUpdateATeamTopicComment,
} from "../utils/api";
import { commonButtonStyle, rootPrefix, threatImpactName } from "../utils/const";
import { a11yProps, dateTimeFormat } from "../utils/func.js";

export default function AnalysisTopic(props) {
  const { user, ateam, targetTopic, isAdmin } = props;
  const [editable, setEditable] = useState(null);
  const [newComment, setNewComment] = useState("");
  const [deleteComment, setDeleteComment] = useState(null);
  const [editComment, setEditComment] = useState("");
  const [comments, setComments] = useState([]);
  const [tab, setTab] = useState(0);
  const [topicModalOpen, setTopicModalOpen] = useState(false);
  const [listHeight, setListHeight] = useState(0);
  const [groupsDict, setGroupsDict] = useState({});

  const topics = useSelector((state) => state.topics);

  const { enqueueSnackbar } = useSnackbar();
  const dispatch = useDispatch();

  useEffect(() => {
    reloadComments(targetTopic.topic_id);
    if (topics?.[targetTopic.topic_id]) return;
    dispatch(getTopic(targetTopic.topic_id));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetTopic.topic_id]);

  useEffect(() => {
    const topicListElem = document.getElementById("topicListElem");
    if (topicListElem) {
      setListHeight(topicListElem.offsetHeight);
    }
  }, []);

  const groupsDictKey = (pteamId, tagId) => `${pteamId}:${tagId}`;

  useEffect(() => {
    if (!targetTopic.pteams?.length > 0) return;

    async function fetchPTeamTagGroups() {
      const newDict = { ...groupsDict };
      let needUpdate = false;
      // targetTopic: schemas.ATeamTopicStatus  see api/app/schemas.py for detail
      for (const pteam of targetTopic.pteams) {
        for (const item of pteam.statuses) {
          const key = groupsDictKey(pteam.pteam_id, item.tag.tag_id);
          if (newDict[key]) continue;
          await apiGetPTeamTag(pteam.pteam_id, item.tag.tag_id).then((response) => {
            // response.data: schemas.ExtTagResponse
            // pick group from each reference -- {"references": [{"target": x, "version": y, "group": z}]}
            const groups = new Set(response.data.references?.map((ref) => ref.group) ?? []);
            newDict[key] = [...groups].sort();
          });
          needUpdate = true;
        }
      }
      if (needUpdate) setGroupsDict(newDict); // explicit update to force re-render
    }

    fetchPTeamTagGroups();
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [targetTopic.topic_id]);

  const operationError = (error) =>
    enqueueSnackbar(
      "Operation failed: " +
        `${error.response.status} ${error.response.statusText} ${error.response.data?.detail}`,
      { variant: "error" }
    );

  const handleChangeTab = (_, newTab) => setTab(newTab);

  const reloadComments = async (topicId) => {
    await apiGetATeamTopicComments(ateam.ateam_id, topicId)
      .then((response) => setComments(response.data))
      .catch((error) => operationError(error));
  };

  const handleCreateComment = async () => {
    if (newComment.trim().length === 0) {
      enqueueSnackbar("Invalid comment", { variant: "error" });
      return;
    }
    await apiCreateATeamTopicComment(ateam.ateam_id, targetTopic.topic_id, {
      comment: newComment.trim(),
    })
      .then(() => {
        reloadComments(targetTopic.topic_id);
        setNewComment("");
      })
      .catch((error) => operationError(error));
  };

  const handleUpdateComment = async (commentId) => {
    if (editComment.trim().length === 0) {
      enqueueSnackbar("Invalid comment", { variant: "error" });
      return;
    }
    await apiUpdateATeamTopicComment(ateam.ateam_id, targetTopic.topic_id, commentId, {
      comment: editComment.trim(),
    })
      .then(() => {
        reloadComments(targetTopic.topic_id);
        setEditComment("");
        setEditable(false);
      })
      .catch((error) => operationError(error));
  };

  const pteamLinkURL = (pteam) => {
    const tmpParams = new URLSearchParams();
    tmpParams.set("pteamId", pteam.pteam_id);
    return `${rootPrefix}/?` + tmpParams.toString();
  };

  const pteamTagLinkURL = (pteam, tag) => {
    const tmpParams = new URLSearchParams();
    tmpParams.set("pteamId", pteam.pteam_id);
    return `${rootPrefix}/tags/${tag.tag_id}?` + tmpParams.toString();
  };
  const topicDetail = topics?.[targetTopic.topic_id];

  /* block rendering until data ready */
  if (!ateam.ateam_id || !topicDetail) return <>Loading...</>;

  const pteamContactInfoDict = ateam.pteams.reduce(
    (dict, pteam) => ({
      ...dict,
      [pteam.pteam_id]: pteam.contact_info || "(no contact info)",
    }),
    {}
  );

  const warningMessageForPTeam = (pteam) =>
    `Contact the unresponsive team: ${pteamContactInfoDict[pteam.pteam_id]}`;

  return (
    <>
      <Box flexGrow={1}>
        <Box m={3}>
          <Box display="flex">
            <ThreatImpactChip
              threatImpact={threatImpactName[topicDetail.threat_impact]}
              sx={{ marginRight: "10px" }}
            />
            <Typography variant="h6" fontWeight={900} mr={1}>
              {topicDetail.title}
            </Typography>
          </Box>
          <UUIDTypography sx={{ marginLeft: "95px" }}>{topicDetail.topic_id}</UUIDTypography>
        </Box>
        <Box borderBottom={1} borderBottomColor="divider" mb={3} mr={1} ml={1}>
          <Tabs aria-label="tabs" onChange={handleChangeTab} value={tab}>
            <Tab label="unsolved" {...a11yProps(0)} />
            <Tab label="overview" {...a11yProps(1)} />
          </Tabs>
        </Box>
        {/* Unsolved tab */}
        <TabPanel index={0} value={tab}>
          <Box sx={{ height: listHeight, minHeight: "700px", overflowY: "scroll" }}>
            {/* Unsolved pteam table */}
            <Box alignItems="baseline" display="flex" flexDirection="columns" mb={2}>
              <Typography mr={2} fontWeight={900}>
                Unsolved pteam
              </Typography>
            </Box>
            <TableContainer component={Paper}>
              <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ width: "30%", fontWeight: 900 }}>PTEAM NAME</TableCell>
                    <TableCell sx={{ fontWeight: 900 }}>TARGET ARTIFACT</TableCell>
                    <TableCell sx={{ fontWeight: 900 }}>TARGET ARTIFACT GROUP</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {targetTopic.pteams.map((pteam) =>
                    pteam.statuses.map((topicStatus, index) => (
                      <TableRow
                        sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                        key={index}
                      >
                        <TableCell sx={{ overflowWrap: "anywhere" }}>
                          <Link href={pteamLinkURL(pteam)} color="inherit">
                            {pteam.pteam_name}
                          </Link>
                          {topicStatus.topic_status === "alerted" && (
                            <WarningTooltip message={warningMessageForPTeam(pteam)} />
                          )}
                        </TableCell>
                        <TableCell align="left">
                          <Link href={pteamTagLinkURL(pteam, topicStatus.tag)}>
                            <Chip
                              label={topicStatus.tag.tag_name}
                              sx={{ borderRadius: "3px", marginleft: "15px" }}
                              size="small"
                            />
                          </Link>
                        </TableCell>
                        <TableCell align="left">
                          {(
                            groupsDict[groupsDictKey(pteam.pteam_id, topicStatus.tag.tag_id)] ?? []
                          ).map((group, index) => (
                            <Typography key={index} sx={{ overflowWrap: "anywhere" }}>
                              {group}
                            </Typography>
                          ))}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            {/* Comments */}
            <Box alignItems="baseline" display="flex" flexDirection="column" mt={5} mb={2}>
              <Typography mr={2} mb={2} fontWeight={900}>
                Comments
              </Typography>
              <TextField
                id="outlined-multiline-static"
                multiline
                fullWidth
                rows={3}
                placeholder="Add new comment..."
                value={newComment}
                onChange={(event) => setNewComment(event.target.value)}
              />
              <Button
                onClick={handleCreateComment}
                sx={{
                  margin: "10px 0 30px auto",
                  ...commonButtonStyle,
                }}
              >
                Comment
              </Button>
              {comments.map((comment, index) => (
                <Box key={index} mb={2} sx={{ width: 1 }}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Typography variant="subtitle2" fontWeight="900" mr={2}>
                      {comment.email}
                    </Typography>
                    <Typography variant="subtitle2">
                      {dateTimeFormat(comment.created_at)}
                    </Typography>
                    {comment.updated_at && (
                      <Typography variant="subtitle2" sx={{ ml: 1 }}>
                        {`(updated at ${dateTimeFormat(comment.updated_at)})`}
                      </Typography>
                    )}
                  </Box>
                  <Box mb={1} sx={{ backgroundColor: grey[100], padding: "10px" }}>
                    {editable === index ? (
                      <TextField
                        id="outlined-multiline-static"
                        multiline
                        fullWidth
                        rows={3}
                        defaultValue={comment.comment}
                        onChange={(event) => setEditComment(event.target.value)}
                        sx={{ backgroundColor: "white" }}
                      />
                    ) : (
                      <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                        {comment.comment}
                      </Typography>
                    )}
                    <Box>
                      {(isAdmin || comment.user_id === user.user_id) && (
                        <Box mt={2}>
                          {editable === index ? (
                            <Box display="flex" justifyContent="flex-end">
                              <Button
                                sx={{
                                  textTransform: "none",
                                  marginRight: 1,
                                }}
                                onClick={() => setEditable(null)}
                              >
                                Cancel
                              </Button>
                              <Button
                                onClick={() => handleUpdateComment(comment.comment_id)}
                                sx={{
                                  ...commonButtonStyle,
                                }}
                              >
                                Edit
                              </Button>
                            </Box>
                          ) : (
                            <>
                              {comment.user_id === user.user_id && (
                                <IconButton
                                  aria-label="delete"
                                  size="small"
                                  onClick={() => {
                                    setEditable(index);
                                  }}
                                >
                                  <EditIcon fontSize="inherit" />
                                </IconButton>
                              )}
                              <IconButton
                                aria-label="delete"
                                size="small"
                                onClick={() => setDeleteComment(comment)}
                              >
                                <DeleteIcon fontSize="inherit" />
                              </IconButton>
                            </>
                          )}
                        </Box>
                      )}
                    </Box>
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        </TabPanel>
        {/* Overview tab */}
        <TabPanel index={1} value={tab}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box display="flex" flexDirection="column">
              <Box>
                {topicDetail.actions?.filter((action) => action.recommended).length > 0 && (
                  <Box mb={3}>
                    <Box alignItems="baseline" display="flex" flexDirection="columns" mb={2}>
                      <Typography mr={2} fontWeight={900}>
                        Recommended actions
                      </Typography>
                      <Chip
                        size="small"
                        label={topicDetail.actions.filter((action) => action.recommended).length}
                        sx={{ marginLeft: "5px", backgroundColor: "#ffef62", fontWeight: 900 }}
                      ></Chip>
                    </Box>
                    {topicDetail.actions
                      .filter((action) => action.recommended)
                      .map((action) => (
                        <ActionItem
                          key={action.action_id}
                          action={action.action}
                          actionId={action.action_id}
                          actionType={action.action_type}
                          recommended={action.recommended}
                          zones={action.zones}
                        />
                      ))}
                  </Box>
                )}
              </Box>
              {topicDetail.actions?.filter((action) => !action.recommended).length > 0 && (
                <Box mb={3}>
                  <Box alignItems="baseline" display="flex" flexDirection="columns" mb={2}>
                    <Typography mr={2} fontWeight={900}>
                      Other actions
                    </Typography>
                    <Chip
                      size="small"
                      label={topicDetail.actions.filter((action) => !action.recommended).length}
                      sx={{ marginLeft: "5px", backgroundColor: "#ffef62", fontWeight: 900 }}
                    ></Chip>
                  </Box>
                  {topicDetail.actions
                    .filter((action) => !action.recommended)
                    .map((action) => (
                      <ActionItem
                        key={action.action_id}
                        action={action.action}
                        actionId={action.action_id}
                        actionType={action.action_type}
                        recommended={action.recommended}
                        zones={action.zones}
                      />
                    ))}
                </Box>
              )}
              {topicDetail.tags.length > 0 && (
                <Box>
                  <Typography fontWeight={900} mt={3} mb={2}>
                    Tags
                  </Typography>
                  <Box mb={5}>
                    {topicDetail.tags.map((tag) => (
                      <Chip
                        key={tag.tag_id}
                        label={tag.tag_name}
                        sx={{ mr: 1, borderRadius: "3px" }}
                        size="small"
                      />
                    ))}
                  </Box>
                </Box>
              )}
              {topicDetail.misp_tags.length > 0 && (
                <Box>
                  <Typography fontWeight={900} mt={3} mb={2}>
                    MISP tags
                  </Typography>
                  <Box mb={5}>
                    {topicDetail.misp_tags.map((mispTag) => (
                      <Chip
                        key={mispTag.tag_id}
                        label={mispTag.tag_name}
                        sx={{ mr: 1, borderRadius: "3px" }}
                        size="small"
                      />
                    ))}
                  </Box>
                </Box>
              )}
              {topicDetail.abstract && (
                <>
                  <Typography fontWeight={900} mb={2}>
                    Detail
                  </Typography>
                  <Typography variant="body">{topicDetail.abstract}</Typography>
                </>
              )}
            </Box>
            <IconButton onClick={() => setTopicModalOpen(true)}>
              <EditIcon />
            </IconButton>
            {/*TODO: fix bug in TopicModal*/}
            <TopicModal
              open={topicModalOpen}
              setOpen={setTopicModalOpen}
              presetTopicId={targetTopic.topic_id}
            />
          </Box>
        </TabPanel>
      </Box>
      <CommentDeleteModal
        comment={deleteComment}
        onClose={() => {
          setDeleteComment(null);
          reloadComments(targetTopic.topic_id);
        }}
      />
    </>
  );
}

AnalysisTopic.propTypes = {
  user: PropTypes.object.isRequired,
  ateam: PropTypes.object.isRequired,
  targetTopic: PropTypes.object.isRequired,
  isAdmin: PropTypes.bool,
};
AnalysisTopic.defaultProps = {
  isAdmin: false,
};
