import PropTypes from "prop-types";
import React from "react";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useGetPTeamMembersQuery,
  useGetPTeamTopicActionsQuery,
  useGetTagsQuery,
  useGetTicketsQuery,
  useGetTopicQuery,
} from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";
import { isRelatedAction } from "../../../utils/topicUtils.js";

import { TopicTableRowView } from "./TopicTableRowView.jsx";

export function TopicTableRow(props) {
  const { pteamId, serviceId, tagId, topicId, references } = props;

  const skipByAuth = useSkipUntilAuthUserIsReady();

  const skipByPTeamId = pteamId === undefined;
  const skipByServiceId = serviceId === undefined;
  const skipByTopicId = topicId === undefined;
  const skipBytagId = tagId === undefined;

  const {
    data: allTags,
    error: allTagsError,
    isLoading: allTagsIsLoading,
  } = useGetTagsQuery(undefined, { skipByAuth });

  const {
    data: members,
    error: membersError,
    isLoading: membersIsLoading,
  } = useGetPTeamMembersQuery(pteamId, { skip: skipByAuth || skipByPTeamId });

  const {
    data: topic,
    error: topicError,
    isLoading: topicIsLoading,
  } = useGetTopicQuery(topicId, { skip: skipByAuth || skipByTopicId });

  const {
    data: pteamTopicActionsData,
    error: pteamTopicActionsError,
    isLoading: pteamTopicActionsIsLoading,
  } = useGetPTeamTopicActionsQuery(
    { topicId, pteamId },
    { skip: skipByAuth || skipByPTeamId || skipByTopicId },
  );

  const {
    data: tickets,
    error: ticketsRelatedToServiceTopicTagError,
    isLoading: ticketsRelatedToServiceTopicTagIsLoading,
  } = useGetTicketsQuery(
    { pteamId, serviceId, topicId, tagId },
    { skip: skipByAuth || skipByPTeamId || skipByServiceId || skipByTopicId || skipBytagId },
  );

  if (skipByAuth || skipByPTeamId || skipByServiceId || skipByTopicId || skipBytagId) return <></>;
  if (allTagsError) throw new APIError(errorToString(allTagsError), { api: "getAllTags" });
  if (allTagsIsLoading) return <>Now loading allTags...</>;
  if (membersError) throw new APIError(errorToString(membersError), { api: "getPTeamMembers" });
  if (membersIsLoading) return <>Now loading PTeamMembers...</>;
  if (topicError) throw new APIError(errorToString(topicError), { api: "getTopic" });
  if (topicIsLoading) return <>Now loading Topic...</>;
  if (pteamTopicActionsError)
    throw new APIError(errorToString(pteamTopicActionsError), { api: "getPTeamTopicActions" });
  if (pteamTopicActionsIsLoading) return <>Now loading topicActions...</>;
  if (ticketsRelatedToServiceTopicTagError)
    throw new APIError(errorToString(ticketsRelatedToServiceTopicTagError), {
      api: "getTicketsRelatedToServiceTopicTag",
    });
  if (ticketsRelatedToServiceTopicTagIsLoading) return <>Now loading tickets...</>;

  const currentTagDict = allTags.find((tag) => tag.tag_id === tagId);
  const topicActions = pteamTopicActionsData.actions?.filter(
    (action) =>
      isRelatedAction(action, references, currentTagDict.tag_name) ||
      isRelatedAction(action, references, currentTagDict.parent_name),
  );

  return (
    <TopicTableRowView
      pteamId={pteamId}
      serviceId={serviceId}
      tagId={tagId}
      topicId={topicId}
      allTags={allTags}
      members={members}
      references={references}
      topic={topic}
      topicActions={topicActions}
      tickets={tickets}
    />
  );
}
TopicTableRow.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  tagId: PropTypes.string.isRequired,
  topicId: PropTypes.string.isRequired,
  references: PropTypes.array.isRequired,
};
