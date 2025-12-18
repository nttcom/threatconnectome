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

export const utcStringToLocalDate = (utcString, includeTimezone) => {
  if (!utcString) return null;
  const date = new Date(utcString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");

  if (!includeTimezone) {
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
  }

  const offsetMinutes = date.getTimezoneOffset();
  const absOffset = Math.abs(offsetMinutes);
  const offsetSign = offsetMinutes <= 0 ? "+" : "-";
  const offsetHours = String(Math.floor(absOffset / 60)).padStart(2, "0");
  const offsetMins = String(absOffset % 60).padStart(2, "0");
  const offsetStr = `${offsetSign}${offsetHours}:${offsetMins}`;
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}${offsetStr}`;
};

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

export const searchWorstSSVC = (tickets) => {
  if (!tickets || tickets.length === 0) {
    return null;
  }

  const result = tickets.reduce((worstSSVC, ticket) => {
    if (compareSSVCPriority(worstSSVC, ticket.ssvc_deployer_priority) === 1) {
      return ticket.ssvc_deployer_priority;
    }
    return worstSSVC;
  }, tickets[0].ssvc_deployer_priority);

  return result;
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
