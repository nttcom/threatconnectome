import { addMinutes, format } from "date-fns";

import { cvssRatings } from "./const";

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

export const utcStringToLocalDate = (utcString) => {
  try {
    const tmpDate = new Date(utcString);
    return addMinutes(tmpDate, -tmpDate.getTimezoneOffset());
  } catch (error) {
    return null;
  }
};

export const pickParentTagName = (tagName) => {
  const tokens = tagName.split(":");
  if (tokens.length < 3) return null;
  return tokens.slice(0, -1).join(":") + ":"; // trim the right most token
};

export const validateNotEmpty = (str) => str?.length > 0;
export const validateUUID = (str) =>
  str?.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$/i);

export const errorToString = (error) => {
  if (typeof error === "string") return error;
  if (error.status && error.data?.detail) {
    // RTKQ
    if (typeof error.data?.detail === "string") return `${error.status}: ${error.data.detail}`;
    return `${error.status}: ${JSON.stringify(error.data.detail)}`; // maybe 422
  }
  if (typeof error.response?.data?.detail === "string")
    // error message from api
    return error.response.data.detail;
  if (error.response?.status && error.response.statusText)
    // maybe 422 by Pydantic
    return `${error.response?.status}: ${error.response?.statusText}`;
  return JSON.stringify(error); // not expected case
};

export const tagsMatched = (allowedTags, actualTags) => {
  if (allowedTags.length === 0 && actualTags.length === 0) return true;
  const actualTagsWithParents = new Set(
    actualTags.reduce((ret, tag) => {
      const parentTag = pickParentTagName(tag);
      if (parentTag === null || parentTag === tag) return [...ret, tag];
      return [...ret, tag, parentTag];
    }, []),
  );
  return [...actualTagsWithParents].some((item) => allowedTags.includes(item));
};

export const setEquals = (set1, set2) =>
  set1.size === set2.size && Array.from(set1).every((val) => set2.has(val));

export const blobToDataURL = async (blob) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => resolve(event.target.result);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(blob);
  });

export const compareSSVCPriority = (prio1, prio2) => {
  const toIntDict = {
    immediate: 1,
    Immediate: 1,
    out_of_cycle: 2,
    "Out-of-cycle": 2,
    scheduled: 3,
    Scheduled: 3,
    defer: 4,
    Defer: 4,
    safe: 4,
    Safe: 4,
    empty: 4,
    Empty: 4,
  };
  const [int1, int2] = [toIntDict[prio1], toIntDict[prio2]];
  if (int1 === int2) return 0;
  else if (int1 < int2) return -1;
  else return 1;
};

export const SearchWorstSSVC = (tickets) => {
  let worstSSVC = tickets[0].ssvc_deployer_priority;
  for (let i = 1; i < tickets.length; i++) {
    if (compareSSVCPriority(worstSSVC, tickets[i].ssvc_deployer_priority) === 1) {
      worstSSVC = tickets[i].ssvc_deployer_priority;
    }
  }
  return worstSSVC;
};

export const cvssConvertToName = (cvssScore) => {
  let rating;
  if (0 < cvssScore && cvssScore < 4.0) {
    rating = "Low";
  } else if (4.0 <= cvssScore && cvssScore < 7.0) {
    rating = "Medium";
  } else if (7.0 <= cvssScore && cvssScore < 9.0) {
    rating = "High";
  } else if (9.0 <= cvssScore && cvssScore <= 10.0) {
    rating = "Critical";
  } else {
    rating = "None";
  }
  return rating;
};

export const cvssConvertToScore = (cvssName) => {
  const rating = cvssRatings[cvssName];
  if (rating) {
    return [rating.min, rating.max];
  }
  return [undefined, undefined];
};

export const checkAdmin = (member, pteamId) => {
  return member.pteam_roles.some(
    (pteam_role) => pteam_role.pteam.pteam_id === pteamId && pteam_role.is_admin,
  );
};

export const countFullWidthAndHalfWidthCharacters = (string) => {
  let count = 0;
  for (let i = 0; i < string.length; i++) {
    const char = string[i];
    if (string[i].match(/[ -~｡-ﾟ]/)) {
      // half-width characters
      count += 1;
    } else {
      // full-width characters
      count += 2;
    }
  }

  return count;
};
