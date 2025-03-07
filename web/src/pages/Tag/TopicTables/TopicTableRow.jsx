import PropTypes from "prop-types";
import React, { useState } from "react";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useGetDependenciesQuery,
  useGetPTeamTopicActionsQuery,
  useGetTagsQuery,
  useGetTicketsQuery,
  useGetTopicQuery,
} from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";

import { TopicTableRowView } from "./TopicTableRowView.jsx";

export function TopicTableRow(props) {
  const { pteamId, serviceId, tagId, topicId } = props;

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
    data: serviceDependencies,
    error: serviceDependenciesError,
    isLoading: serviceDependenciesIsLoading,
  } = useGetDependenciesQuery(
    { pteamId, serviceId },
    { skip: skipByAuth || skipByPTeamId || skipByServiceId },
  );

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
  if (serviceDependenciesError)
    throw new APIError(errorToString(serviceDependenciesError), { api: "getServiceDependencies" });
  if (serviceDependenciesIsLoading) return <>Now loading serviceDependencies...</>;
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

  return (
    <TopicTableRowView
      pteamId={pteamId}
      serviceId={serviceId}
      tagId={tagId}
      topicId={topicId}
      allTags={allTags}
      serviceDependencies={serviceDependencies}
      topic={topic}
      pteamTopicActionsData={pteamTopicActionsData}
      tickets={tickets}
    />
  );
}
TopicTableRow.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  tagId: PropTypes.string.isRequired,
  topicId: PropTypes.string.isRequired,
};
