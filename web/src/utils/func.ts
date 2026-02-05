import { FetchBaseQueryError } from "@reduxjs/toolkit/query/react";
import { SerializedError } from "@reduxjs/toolkit";

import { UserResponse } from "../../types/types.gen";

export const a11yProps = (index: number) => ({
  id: `tab-${index}`,
  "aria-controls": `tabpanel-${index}`,
});

export const calcTimestampDiff = (timestamp: string) => {
  if (!timestamp) return "-";
  const targetDate = new Date(timestamp);
  const daysAgo = Math.floor((new Date().getTime() - targetDate.getTime()) / (1000 * 60 * 60 * 24));
  switch (daysAgo) {
    case 0:
      return "today";
    case 1:
      return "yesterday";
    default:
      return `${daysAgo} days ago`;
  }
};

export const utcStringToLocalDate = (
  utcString: string | null | undefined,
  includeTimezone: boolean,
) => {
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

export const errorToString = (error: string | SerializedError | FetchBaseQueryError) => {
  if (typeof error === "string") return error;
  if ("status" in error && error.data && typeof error.data === "object" && "detail" in error.data) {
    // RTKQ
    const detail = (error.data as Record<string, unknown>).detail;
    if (typeof detail === "string") return `${error.status}: ${detail}`;
    return `${error.status}: ${JSON.stringify(detail)}`; // maybe 422
  }

  return JSON.stringify(error); // not expected case
};

export const setEquals = (set1: Set<string>, set2: Set<string>) =>
  set1.size === set2.size && Array.from(set1).every((val) => set2.has(val));

export const blobToDataURL = async (blob: Blob) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => resolve(event.target?.result);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(blob);
  });

export const checkAdmin = (member: UserResponse, pteamId: string) => {
  return member.pteam_roles.some(
    (pteam_role) => pteam_role.pteam.pteam_id === pteamId && pteam_role.is_admin,
  );
};

export const countFullWidthAndHalfWidthCharacters = (string: string) => {
  let count = 0;
  for (let i = 0; i < string.length; i++) {
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
