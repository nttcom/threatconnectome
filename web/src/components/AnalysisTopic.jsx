import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from "@mui/icons-material";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
  Box,
  Button,
  Chip,
  Collapse,
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
import { grey, red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";

import { AnalysisActionTypeIcon } from "../components/AnalysisActionTypeIcon";
import { CommentDeleteModal } from "../components/CommentDeleteModal";
import { TabPanel } from "../components/TabPanel";
import { ThreatImpactChip } from "../components/ThreatImpactChip";
import { TopicEditModal } from "../components/TopicEditModal";
import { UUIDTypography } from "../components/UUIDTypography";
import { WarningTooltip } from "../components/WarningTooltip";
import styles from "../cssModule/button.module.css";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import {
  useGetTopicQuery,
  useCreateATeamTopicCommentMutation,
  useGetATeamTopicCommentQuery,
  useGetTopicActionsQuery,
  useUpdateATeamTopicCommentMutation,
  useGetTagsQuery,
} from "../services/tcApi";
import { rootPrefix, threatImpactNames } from "../utils/const";
import { a11yProps, dateTimeFormat, errorToString, tagsMatched } from "../utils/func.js";

export function AnalysisTopic(props) {
  const { user, ateam, targetTopic, isAdmin = false } = props;
  const [editable, setEditable] = useState(null);
  const [newComment, setNewComment] = useState("");
  const [deleteComment, setDeleteComment] = useState(null);
  const [editComment, setEditComment] = useState("");
  const [tab, setTab] = useState(0);
  const [topicModalOpen, setTopicModalOpen] = useState(false);
  const [listHeight, setListHeight] = useState(0);
  const [detailOpen, setDetailOpen] = useState(false);
  const [actionExpanded, setActionExpanded] = useState(false);
  const [createATeamTopicComment] = useCreateATeamTopicCommentMutation();
  const [updateATeamTopicComment] = useUpdateATeamTopicCommentMutation();

  const { enqueueSnackbar } = useSnackbar();

  const box_sx = { mt: 3 };

  const actionhandleChange = (panel) => (event, isExpanded) => {
    setActionExpanded(isExpanded ? panel : false);
  };

  const skip = useSkipUntilAuthTokenIsReady();

  const {
    data: topic,
    error: topicError,
    isLoading: topicIsLoading,
  } = useGetTopicQuery(targetTopic.topic_id, { skip });

  const {
    data: topicActions,
    error: topicActionsError,
    isLoading: topicActionsIsLoading,
  } = useGetTopicActionsQuery(targetTopic.topic_id, { skip });
  const {
    data: comments,
    error: commentsError,
    isLoading: commentsIsLoading,
  } = useGetATeamTopicCommentQuery(
    { ateamId: ateam.ateam_id, topicId: targetTopic.topic_id },
    { skip },
  );
  const {
    data: allTags,
    error: allTagsError,
    isLoading: allTagsIsLoading,
  } = useGetTagsQuery(undefined, { skip: skip || !topicModalOpen });

  useEffect(() => {
    const topicListElem = document.getElementById("topicListElem");
    if (topicListElem) {
      setListHeight(topicListElem.offsetHeight);
    }
  }, []);

  const handleChangeTab = (_, newTab) => setTab(newTab);

  const handleCreateComment = async () => {
    if (newComment.trim().length === 0) {
      enqueueSnackbar("Invalid comment", { variant: "error" });
      return;
    }
    await createATeamTopicComment({
      ateamId: ateam.ateam_id,
      topicId: targetTopic.topic_id,
      data: {
        comment: newComment.trim(),
      },
    })
      .unwrap()
      .then(() => setNewComment(""))
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, {
          variant: "error",
        }),
      );
  };

  const handleUpdateComment = async (commentId) => {
    if (editComment.trim().length === 0) {
      enqueueSnackbar("Invalid comment", { variant: "error" });
      return;
    }
    await updateATeamTopicComment({
      ateamId: ateam.ateam_id,
      topicId: targetTopic.topic_id,
      commentId: commentId,
      data: {
        comment: editComment.trim(),
      },
    })
      .unwrap()
      .then(() => {
        setEditComment("");
        setEditable(false);
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, {
          variant: "error",
        }),
      );
  };

  const pteamServiceTagLinkURL = (pteamId, serviceId, tagId) => {
    const tmpParams = new URLSearchParams();
    tmpParams.set("pteamId", pteamId);
    tmpParams.set("serviceId", serviceId);
    return `${rootPrefix}/tags/${tagId}?` + tmpParams.toString();
  };
  const handleDetailOpen = () => setDetailOpen(!detailOpen);

  /* block rendering until data ready */
  if (skip) return <Box sx={{ m: 2 }}></Box>;
  if (topicError)
    return <Box sx={{ m: 2 }}>{`Cannot get Topic: ${errorToString(topicError)}`}</Box>;
  if (topicIsLoading) return <Box sx={{ m: 2 }}>Now loading Topic...</Box>;
  if (topicActionsError)
    return (
      <Box sx={{ m: 2 }}>{`Cannot get topicActions: ${errorToString(topicActionsError)}`}</Box>
    );
  if (topicActionsIsLoading) return <Box sx={{ m: 2 }}>Now loading topicActions...</Box>;
  if (allTagsError) return <>{`Cannot get allTags: ${errorToString(allTagsError)}`}</>;
  if (allTagsIsLoading) return <>Now loading allTags...</>;

  const topicTagNames = topic.tags.map((tag) => tag.tag_name);
  const recommendedActions = topicActions.filter((action) => action.recommended);
  const otherActions = topicActions.filter((action) => !action.recommended);

  const pteamContactInfoDict = ateam.pteams.reduce(
    (dict, pteam) => ({
      ...dict,
      [pteam.pteam_id]: pteam.contact_info || "(no contact info)",
    }),
    {},
  );

  const warningMessageForPTeam = (pteamId) =>
    `Contact the unresponsive team: ${pteamContactInfoDict[pteamId]}`;
  const sortedStatuses = targetTopic.pteam_statuses ?? [];

  return (
    <>
      <Box flexGrow={1}>
        <Box m={3}>
          <Box display="flex">
            <ThreatImpactChip
              threatImpact={threatImpactNames[topic.threat_impact]}
              sx={{ marginRight: "10px" }}
            />
            <Typography variant="h6" fontWeight={900} mr={1}>
              {topic.title}
            </Typography>
            <Box flexGrow={1} />
            <Box>
              <IconButton onClick={() => setTopicModalOpen(true)}>
                <EditIcon />
              </IconButton>
            </Box>
          </Box>
          <UUIDTypography sx={{ marginLeft: "95px" }}>{topic.topic_id}</UUIDTypography>
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
                    <TableCell sx={{ fontWeight: 900 }}>TARGET ARTIFACT SERVICE</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sortedStatuses.map((pteamStatus) =>
                    pteamStatus.service_statuses.map((serviceStatus) => (
                      <TableRow
                        sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                        key={serviceStatus.service_id}
                      >
                        <TableCell sx={{ overflowWrap: "anywhere" }}>
                          <Link
                            href={pteamServiceTagLinkURL(
                              pteamStatus.pteam_id,
                              serviceStatus.service_id,
                              serviceStatus.tag.tag_id,
                            )}
                            color="inherit"
                          >
                            {pteamStatus.pteam_name}
                          </Link>
                          {serviceStatus.topic_status === "alerted" && (
                            <WarningTooltip
                              message={warningMessageForPTeam(pteamStatus.pteam_id)}
                            />
                          )}
                        </TableCell>
                        <TableCell align="left">
                          <Chip
                            label={serviceStatus.tag.tag_name}
                            sx={{ borderRadius: "3px", marginleft: "15px" }}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="left">
                          <Typography sx={{ overflowWrap: "anywhere" }}>
                            {serviceStatus.service_name}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )),
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
                className={styles.check_btn}
                onClick={handleCreateComment}
                sx={{
                  margin: "10px 0 30px auto",
                }}
              >
                Comment
              </Button>
              {commentsError && (
                <>{`Cannot get ATeamTopicComment: ${errorToString(commentsError)}`}</>
              )}
              {commentsIsLoading && <>Now loading ATeamTopicComments...</>}
              {(comments ?? []).map((comment, index) => (
                <Box key={comment.comment_id} mb={2} sx={{ width: 1 }}>
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
                                variant="outlined"
                                color="success"
                                onClick={() => handleUpdateComment(comment.comment_id)}
                                sx={{
                                  textTransform: "none",
                                }}
                              >
                                Edit
                              </Button>
                            </Box>
                          ) : (
                            <Box display="flex" justifyContent="flex-end">
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
                            </Box>
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
                <Typography mb={0.5} fontWeight={900}>
                  Tags
                </Typography>
                {topic.tags.length > 0 ? (
                  <Box ml={1}>
                    {topic.tags.map((tag) => (
                      <Chip
                        key={tag.tag_id}
                        label={tag.tag_name}
                        sx={{ mr: 1, borderRadius: "3px" }}
                        size="small"
                      />
                    ))}
                  </Box>
                ) : (
                  <Typography sx={{ color: grey[500] }} ml={1}>
                    No Data
                  </Typography>
                )}
              </Box>
              <Box sx={box_sx}>
                <Box display="flex" flexDirection="columns" justifyContent="space-between">
                  <Typography mb={0.5} fontWeight={900}>
                    MISP Tags
                  </Typography>
                </Box>
                <Box ml={1}>
                  {topic.misp_tags.length > 0 ? (
                    <>
                      {topic.misp_tags.map((mispTag) => (
                        <Chip
                          key={mispTag.tag_id}
                          label={mispTag.tag_name}
                          sx={{ mr: 1, borderRadius: "3px" }}
                          size="small"
                        />
                      ))}
                    </>
                  ) : (
                    <Typography sx={{ color: grey[500] }}>No Data</Typography>
                  )}
                </Box>
              </Box>
              <Box sx={box_sx}>
                <Box display="flex" flexDirection="columns" mb={1}>
                  <Typography mr={0.5} mt={0.5} fontWeight={900}>
                    Details
                  </Typography>
                  {topic.abstract && (
                    <IconButton onClick={handleDetailOpen} size="small">
                      {detailOpen ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  )}
                </Box>
                <Collapse in={detailOpen}>
                  <Box ml={1}>
                    <Typography variant="body">{topic.abstract}</Typography>
                  </Box>
                </Collapse>
                <Box ml={1}>
                  {!topic.abstract && (
                    <Typography variant="body" sx={{ color: grey[500] }}>
                      No Data
                    </Typography>
                  )}
                </Box>
              </Box>
              <Box sx={box_sx}>
                <Box display="flex" flexDirection="columns">
                  <Typography mr={2} fontWeight={900}>
                    Recommended actions
                  </Typography>
                  {recommendedActions?.length > 0 && (
                    <Chip
                      size="small"
                      label={recommendedActions.length}
                      sx={{ marginLeft: "5px", backgroundColor: "#ffef62", fontWeight: 900 }}
                    />
                  )}
                </Box>
                {recommendedActions?.length > 0 ? (
                  <Box mt={1} sx={{ width: "650px" }}>
                    {recommendedActions?.map((action, index) => (
                      <Box key={index}>
                        <Accordion
                          expanded={actionExpanded === action.action}
                          onChange={actionhandleChange(action.action)}
                          square={true}
                        >
                          <AccordionSummary
                            expandIcon={<ExpandMoreIcon />}
                            aria-controls="panel1bh-content"
                            id="panel1bh-header"
                          >
                            <Box display="flex" flexDirection="columns">
                              {tagsMatched(topicTagNames, action.ext?.tags ?? []) ? (
                                <AnalysisActionTypeIcon actionType={action.action_type} />
                              ) : (
                                <Badge
                                  color="error"
                                  variant="dot"
                                  badgeContent=" "
                                  sx={{ marginRight: "10px" }}
                                >
                                  <AnalysisActionTypeIcon actionType={action.action_type} />
                                </Badge>
                              )}
                              {action.action}
                            </Box>
                          </AccordionSummary>
                          <AccordionDetails sx={{ backgroundColor: grey[50] }}>
                            {tagsMatched(topicTagNames, action.ext?.tags ?? []) || (
                              <Box display="flex" flexDirection="columns">
                                <Typography fontWeight={800} sx={{ color: red[500] }}>
                                  The destination does not match the topic.
                                </Typography>
                              </Box>
                            )}
                            <Box display="flex" flexDirection="columns">
                              <Typography fontWeight={300}>ID: </Typography>
                              <Typography>{action.action_id}</Typography>
                            </Box>
                            <Box display="flex" flexDirection="columns">
                              <Typography fontWeight={300}>Type: </Typography>
                              <Chip
                                size="small"
                                label={action.action_type}
                                sx={{
                                  marginLeft: "5px",
                                  backgroundColor: grey[600],
                                  color: "#ffffff",
                                }}
                              />
                            </Box>
                            <Box display="flex" flexDirection="columns">
                              <Typography fontWeight={300}>Author: </Typography>
                              <Typography>{action.created_by}</Typography>
                            </Box>
                            <Box display="flex" flexDirection="columns">
                              <Typography fontWeight={300}>Creation date: </Typography>
                              <Typography>{action.created_at}</Typography>
                            </Box>
                          </AccordionDetails>
                        </Accordion>
                      </Box>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body" ml={1} sx={{ color: grey[500] }}>
                    No Data
                  </Typography>
                )}
              </Box>
              <Box sx={box_sx}>
                <Box display="flex" flexDirection="columns">
                  <Typography mr={2} fontWeight={900}>
                    Other actions
                  </Typography>
                  {otherActions?.length > 0 && (
                    <Chip
                      size="small"
                      label={otherActions.length}
                      sx={{ marginLeft: "5px", backgroundColor: "#ffef62", fontWeight: 900 }}
                    />
                  )}
                </Box>
                {otherActions?.length > 0 ? (
                  <Box mt={1} sx={{ width: "650px" }}>
                    {otherActions.map((action, index) => (
                      <Box key={index}>
                        <Accordion
                          expanded={actionExpanded === action.action}
                          onChange={actionhandleChange(action.action)}
                          square={true}
                        >
                          <AccordionSummary
                            expandIcon={<ExpandMoreIcon />}
                            aria-controls="panel1bh-content"
                            id="panel1bh-header"
                          >
                            <Box display="flex" flexDirection="columns">
                              {tagsMatched(topicTagNames, action.ext?.tags ?? []) ? (
                                <AnalysisActionTypeIcon actionType={action.action_type} />
                              ) : (
                                <Badge
                                  color="error"
                                  variant="dot"
                                  badgeContent=" "
                                  sx={{ marginRight: "10px" }}
                                >
                                  <AnalysisActionTypeIcon actionType={action.action_type} />
                                </Badge>
                              )}
                              {action.action}
                            </Box>
                          </AccordionSummary>
                          <AccordionDetails sx={{ backgroundColor: grey[50] }}>
                            {tagsMatched(topicTagNames, action.ext?.tags ?? []) || (
                              <Box display="flex" flexDirection="columns">
                                <Typography fontWeight={800} sx={{ color: red[500] }}>
                                  The destination does not match the topic.
                                </Typography>
                              </Box>
                            )}
                            <Box display="flex" flexDirection="columns">
                              <Typography fontWeight={300}>ID: </Typography>
                              <Typography>{action.action_id}</Typography>
                            </Box>
                            <Box display="flex" flexDirection="columns">
                              <Typography fontWeight={300}>Type: </Typography>
                              <Chip
                                size="small"
                                label={action.action_type}
                                sx={{
                                  marginLeft: "5px",
                                  backgroundColor: grey[600],
                                  color: "#ffffff",
                                }}
                              />
                            </Box>
                            <Box display="flex" flexDirection="columns">
                              <Typography fontWeight={300}>Author: </Typography>
                              <Typography>{action.created_by}</Typography>
                            </Box>
                            <Box display="flex" flexDirection="columns">
                              <Typography fontWeight={300}>Creation date: </Typography>
                              <Typography>{action.created_at}</Typography>
                            </Box>
                          </AccordionDetails>
                        </Accordion>
                      </Box>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body" ml={1} sx={{ color: grey[500] }}>
                    No Data
                  </Typography>
                )}
              </Box>
            </Box>
          </Box>
        </TabPanel>
        {allTags && (
          <TopicEditModal
            open={topicModalOpen}
            onSetOpen={setTopicModalOpen}
            currentTopic={topic}
            currentActions={topicActions}
            allTags={allTags}
          />
        )}
      </Box>
      <CommentDeleteModal comment={deleteComment} onClose={() => setDeleteComment(null)} />
    </>
  );
}

AnalysisTopic.propTypes = {
  user: PropTypes.object.isRequired,
  ateam: PropTypes.object.isRequired,
  targetTopic: PropTypes.object.isRequired,
  isAdmin: PropTypes.bool,
};
