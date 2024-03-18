import {
  AddBox as AddBoxIcon,
  Close as CloseIcon,
  ContentPaste as ContentPasteIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  DialogActions,
  Divider,
  IconButton,
  List,
  Switch,
  Typography,
} from "@mui/material";
import { blue, grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import {
  getPTeamSolvedTaggedTopicIds,
  getPTeamTagsSummary,
  getPTeamTopicActions,
  getPTeamUnsolvedTaggedTopicIds,
} from "../slices/pteam";
import { getTopic } from "../slices/topics";
import { updateTopic, createAction, updateAction, deleteAction } from "../utils/api";
import { actionTypes, modalCommonButtonStyle } from "../utils/const";
import { parseVulnerableVersions, versionMatch } from "../utils/versions";

import { ActionGenerator } from "./ActionGenerator";
import { ActionItem } from "./ActionItem";

export function PTeamEditAction(props) {
  const {
    open,
    onSetOpen,
    presetTopicId,
    presetTagId,
    presetParentTagId,
    presetActions,
    currentTagDict,
    pteamtag,
  } = props;

  const [errors, setErrors] = useState([]);

  const { enqueueSnackbar } = useSnackbar();

  const user = useSelector((state) => state.user.user);
  const pteamId = useSelector((state) => state.pteam.pteamId);
  const topics = useSelector((state) => state.topics.topics);
  const allTags = useSelector((state) => state.tags.allTags); // dispatched by parent

  const src = topics[presetTopicId];
  const [topicId, setTopicId] = useState("");
  const [title, setTitle] = useState("");
  const [abst, setAbst] = useState("");
  const [threatImpact, setThreatImpact] = useState(4);
  const [tagIds, setTagIds] = useState([]);
  const [mispTags, setMispTags] = useState("");
  const [actionTagOptions, setActionTagOptions] = useState([]);
  const [actions, setActions] = useState([]);
  const [editActionOpen, setEditActionOpen] = useState(false);
  const [editActionTarget, setEditActionTarget] = useState({});
  const [actionFilter, setActionFilter] = useState(true);

  const dispatch = useDispatch();

  useEffect(() => {
    setErrors([]);
    setTopicId(presetTopicId ?? "");
    setTitle(src?.title ?? "");
    setAbst(src?.abstract ?? "");
    setThreatImpact(src?.threat_impact ?? 4);
    setTagIds(
      src?.tags
        ? src.tags.map((tag) => tag.tag_id)
        : presetParentTagId
          ? [presetParentTagId]
          : presetTagId
            ? [presetTagId]
            : [],
    );
    setMispTags(src?.misp_tags?.map((misp_tag) => misp_tag.tag_name).join(",") ?? "");
    setActionTagOptions([
      ...new Set([
        ...(src?.tags?.map((tag) => tag.tag_id) ?? []),
        ...(presetParentTagId ? [presetParentTagId] : []),
        ...(presetTagId ? [presetTagId] : []),
      ]),
    ]);
    setActions(presetActions ?? []);
    setEditActionOpen(false);
    setEditActionTarget({});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  if (!pteamId || !allTags) return <></>;

  const operationError = (error) => {
    const resp = error.response ?? { status: "???", statusText: error.toString() };
    enqueueSnackbar(`Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`, {
      variant: "error",
    });
  };

  const validateActionTags = () => {
    const validTagNames = new Set();
    const presetTag = allTags.find((tag) => tag.tag_id === presetTagId);
    validTagNames.add(presetTag.tag_name);

    allTags
      .filter((tag) => tagIds.includes(tag.tag_id))
      .forEach((tag) => {
        validTagNames.add(tag.tag_name);
        if (tag.parent_name && tag.parent_name !== tag.tag_name) {
          validTagNames.add(tag.parent_name);
        }
      });
    for (let action of actions) {
      if (action.ext?.tags && !action.ext.tags.every((tag) => validTagNames.has(tag))) {
        enqueueSnackbar(`Some of the ActionTags "${action.ext.tags}" are not TopicTags`, {
          variant: "error",
        });
        return false;
      }
    }
    return true;
  };

  const reloadTopicAfterAPI = async () => {
    // fix topic state
    await Promise.all([
      dispatch(getTopic(topicId)),
      dispatch(getPTeamTagsSummary(pteamId)),
      dispatch(getPTeamTopicActions({ pteamId: pteamId, topicId: topicId })),
    ]);
    // update only if needed
    if (pteamId && presetTagId) {
      await Promise.all([
        dispatch(getPTeamSolvedTaggedTopicIds({ pteamId: pteamId, tagId: presetTagId })),
        dispatch(getPTeamUnsolvedTaggedTopicIds({ pteamId: pteamId, tagId: presetTagId })),
      ]);
    }
  };

  const handleUpdateTopic = async () => {
    if (!validateActionTags()) return;

    const presetActionIds = new Set(presetActions.map((a) => a.action_id));

    actions.forEach((a) => {
      const actionRequest = {
        ...a,
        topic_id: topicId,
      };
      if (a.action_id === null) {
        createAction(actionRequest).catch((error) => operationError(error));
      } else if (presetActionIds.has(a.action_id)) {
        updateAction(a.action_id, actionRequest).catch((error) => operationError(error));
        presetActionIds.delete(a.action_id);
      }
    });

    // delete actions that are not related to topic
    presetActionIds.forEach((actionId) => {
      deleteAction(actionId).catch((error) => operationError(error));
    });

    if (src.created_by !== user.user_id) {
      enqueueSnackbar(
        "Only actions have been changed, not topics. You can't update topic, because you are not topic creator.",
        { variant: "warning" },
      );
      reloadTopicAfterAPI();
      onSetOpen(false);
      return;
    }

    const data = {
      title: title,
      abstract: abst,
      threat_impact: parseInt(threatImpact),
      tags: allTags.filter((tag) => tagIds.includes(tag.tag_id)).map((tag) => tag.tag_name),
      misp_tags: mispTags?.length > 0 ? mispTags.split(",").map((mispTag) => mispTag.trim()) : [],
    };
    await updateTopic(topicId, data)
      .then(async () => {
        enqueueSnackbar("Update topic succeeded", { variant: "success" });
        reloadTopicAfterAPI();
        onSetOpen(false);
      })
      .catch((error) => operationError(error));
  };

  const handleClose = () => {
    onSetOpen(false);
  };

  function ActionGeneratorModal() {
    const [generatorOpen, setGeneratorOpen] = useState(false);
    return (
      <>
        <IconButton onClick={() => setGeneratorOpen(true)} sx={{ color: blue[700] }}>
          <AddBoxIcon />
        </IconButton>
        <Dialog open={generatorOpen} onClose={() => setGeneratorOpen(false)}>
          <DialogContent>
            <ActionGenerator
              text="Add action"
              tagIds={actionTagOptions}
              onGenerate={(ret) => {
                setActions([...actions, ret]);
                setGeneratorOpen(false);
              }}
              onCancel={() => setGeneratorOpen(false)}
            />
          </DialogContent>
        </Dialog>
      </>
    );
  }

  // TODO: make common function around action filter
  const isRelatedAction = (action, tagName) =>
    (!action.ext?.tags?.length > 0 || action.ext.tags.includes(tagName)) &&
    (!action.ext?.vulnerable_versions?.[tagName]?.length > 0 ||
      parseVulnerableVersions(action.ext.vulnerable_versions[tagName]).some(
        (actionVersion) =>
          !pteamtag.references?.length > 0 ||
          pteamtag.references?.some((ref) =>
            versionMatch(
              ref.version,
              actionVersion.ge,
              actionVersion.gt,
              actionVersion.le,
              actionVersion.lt,
              actionVersion.eq,
              true,
            ),
          ),
      ));

  // TODO: make common function around action filter
  const topicActions = actionFilter
    ? actions?.filter(
        (action) =>
          isRelatedAction(action, currentTagDict.tag_name) ||
          isRelatedAction(action, currentTagDict.parent_name),
      )
    : actions ?? [];

  return (
    <>
      <Dialog open={open === true} fullWidth>
        <DialogTitle>
          <Box alignItems="center" display="flex" flexDirection="row">
            <Typography flexGrow={1} variant="inherit">
              Edit actions on this topic
            </Typography>
            <IconButton onClick={handleClose} sx={{ color: grey[500] }}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <Divider />
        <DialogContent>
          <>
            <Box flexDirection="row">
              <Box display="flex" flexDirection="column">
                <Box mb={1}>
                  <Box display="flex" flexDirection="row" alignItems="center" mb={1}>
                    <Typography>Add New Actions</Typography>
                    <ActionGeneratorModal />
                    <Box sx={{ flex: "2 1 auto" }} />
                    <Switch
                      checked={actionFilter}
                      onChange={() => setActionFilter(!actionFilter)}
                      size="small"
                      color="success"
                      sx={{ marginLeft: 28 }}
                    />
                    <Typography>Action filter</Typography>
                  </Box>
                  {topicActions?.length > 0 || (
                    <Box
                      display="flex"
                      flexDirection="row"
                      alignItems="center"
                      sx={{ color: grey[500] }}
                    >
                      <ContentPasteIcon fontSize="small" sx={{ mr: 0.5 }} />
                      <Typography variant="body2">Please add action</Typography>
                    </Box>
                  )}
                  <List
                    sx={{
                      width: "100%",
                      position: "relative",
                      overflow: "auto",
                      maxHeight: 150,
                    }}
                  >
                    {topicActions &&
                      topicActions
                        .slice()
                        .sort(
                          (a, b) =>
                            actionTypes.indexOf(a.action_type) - actionTypes.indexOf(b.action_type),
                        )
                        .map((action, idx) => (
                          <ActionItem
                            key={idx}
                            action={action.action}
                            actionId={action.action_id}
                            actionType={action.action_type}
                            recommended={action.recommended}
                            ext={action.ext}
                            onChangeRecommended={() =>
                              setActions(
                                actions.map((item) =>
                                  item !== action
                                    ? item
                                    : { ...item, recommended: !item.recommended },
                                ),
                              )
                            }
                            onDelete={() => setActions(actions.filter((item) => item !== action))}
                            sx={{ flexGrow: 1 }}
                          />
                        ))}
                  </List>
                </Box>
              </Box>
            </Box>
          </>
        </DialogContent>
        <DialogActions>
          <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
            <Button
              onClick={handleUpdateTopic}
              disabled={errors?.length > 0}
              sx={modalCommonButtonStyle}
            >
              Update
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
      <Dialog open={editActionOpen} onClose={() => setEditActionOpen(false)}>
        <DialogContent>
          <ActionGenerator
            text="Update action"
            tagIds={actionTagOptions}
            action={editActionTarget}
            onEdit={(ret) => {
              setActions(actions.map((item) => (item !== editActionTarget ? item : ret)));
              setEditActionOpen(false);
            }}
            onCancel={() => setEditActionOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

PTeamEditAction.propTypes = {
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
  presetTopicId: PropTypes.string,
  presetTagId: PropTypes.string,
  presetParentTagId: PropTypes.string,
  presetActions: PropTypes.arrayOf(
    PropTypes.shape({
      action_id: PropTypes.string,
      action: PropTypes.string,
      action_type: PropTypes.string,
      recommended: PropTypes.bool,
      ext: PropTypes.shape({
        tags: PropTypes.array,
        vulnerable_versions: PropTypes.object,
      }),
    }),
  ),
  currentTagDict: PropTypes.object.isRequired,
  pteamtag: PropTypes.object.isRequired,
};
