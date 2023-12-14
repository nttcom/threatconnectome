import moment from "moment";

import { getZonedTeams } from "./api";

export const a11yProps = (index) => ({
  id: `tab-${index}`,
  "aria-controls": `tabpanel-${index}`,
});

export const calcTimestampDiff = (timestamp) => {
  if (!timestamp) return "-";
  const targetDate = new Date(timestamp);
  const daysAgo = Math.floor((new Date() - targetDate) / (1000 * 60 * 60 * 24));
  switch (daysAgo) {
    case 0:
      return "today";
    case 1:
      return "yesterday";
    default:
      return `${daysAgo} days ago`;
  }
};

export const dateTimeFormat = (timestamp) => {
  return moment.utc(timestamp).local().format();
};

export const pickParentTagName = (tagName) => {
  const tokens = tagName.split(":");
  if (tokens.length < 3) return null;
  return tokens.slice(0, -1).join(":") + ":"; // trim the right most token
};

export const pickMismatchedTopicActionTags = (topicTagNames, actionTagNames) => {
  const mismatchedTagNames = actionTagNames.reduce(
    (ret, actionTagName) => [
      ...ret,
      ...(topicTagNames.includes(actionTagName) ||
      topicTagNames.includes(pickParentTagName(actionTagName))
        ? []
        : [actionTagName]),
    ],
    []
  );
  return mismatchedTagNames;
};

export const validateNotEmpty = (str) => str?.length > 0;
export const validateUUID = (str) =>
  str?.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$/i);

export const errorToString = (error) =>
  typeof error.response?.data?.detail === "string"
    ? error.response.data.detail
    : `${error.response?.status}: ${error.response?.statusText}`; // maybe 422 by Pydantic

export const tagsMatched = (allowedTags, actualTags) => {
  if (allowedTags.length === 0 && actualTags.length === 0) return true;
  const actualTagsWithParents = new Set(
    actualTags.reduce((ret, tag) => {
      const parentTag = pickParentTagName(tag);
      if (parentTag === null || parentTag === tag) return [...ret, tag];
      return [...ret, tag, parentTag];
    }, [])
  );
  return [...actualTagsWithParents].some((item) => allowedTags.includes(item));
};

export const setEquals = (set1, set2) =>
  set1.size === set2.size && Array.from(set1).every((val) => set2.has(val));

export const collectZonesRelatedTeams = async (zoneNames) => {
  if (!zoneNames.length > 0) return { ateams: {}, pteams: {}, unvisibleExists: false };

  const results = await Promise.allSettled(zoneNames.map((zoneName) => getZonedTeams(zoneName)));
  const fails = results.filter((result) => result.status !== "fulfilled");
  if (fails.length > 0) {
    const unexpectedErrors = fails.filter((fail) => fail.reason?.response?.status !== 403);
    if (unexpectedErrors.length > 0) throw unexpectedErrors[0].reason ?? new Error("Unknown Error");
  }
  const emptyResult = { ateams: {}, pteams: {}, unvisibleExists: fails.length > 0 };

  return results
    .filter((result) => result.status === "fulfilled")
    .map((solved) => solved.value.data)
    .reduce(
      (ret, teamData) => ({
        ...ret,
        ateams: {
          ...ret.ateams,
          ...teamData.ateams.reduce(
            (newATeams, ateam) => ({
              ...newATeams,
              [ateam.ateam_id]: ateam,
            }),
            {}
          ),
        },
        pteams: {
          ...ret.pteams,
          ...teamData.pteams.reduce(
            (newPTeams, pteam) => ({
              ...newPTeams,
              [pteam.pteam_id]: pteam,
            }),
            {}
          ),
        },
      }),
      emptyResult
    );
};
