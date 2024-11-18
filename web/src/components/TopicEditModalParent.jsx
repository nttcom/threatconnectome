import PropTypes from "prop-types";
import React from "react";

import { TopicEditModalChild } from "../components/TopicEditModalChild";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetTagsQuery } from "../services/tcApi";
import { errorToString } from "../utils/func";

export function TopicEditModalParent(props) {
  const { open, onSetOpen, currentTopic, currentActions } = props;

  const skip = useSkipUntilAuthTokenIsReady();
  const {
    data: allTags,
    error: allTagsError,
    isLoading: allTagsIsLoading,
  } = useGetTagsQuery(undefined, { skip });

  if (allTagsError) return <>{`Cannot get allTags: ${errorToString(allTagsError)}`}</>;
  if (allTagsIsLoading) return <>Now loading allTags...</>;

  return (
    <TopicEditModalChild
      open={open}
      onSetOpen={onSetOpen}
      currentTopic={currentTopic}
      currentActions={currentActions}
      allTags={allTags}
    />
  );
}

TopicEditModalParent.propTypes = {
  open: PropTypes.bool.isRequired,
  onSetOpen: PropTypes.func.isRequired,
  currentTopic: PropTypes.object.isRequired,
  currentActions: PropTypes.array.isRequired,
};
