import type { TFunction } from "i18next";

import { maxKeywordLengthInHalf, maxKeywords } from "../const";
import { countFullWidthAndHalfWidthCharacters } from "../func";

function maxLengthParams(maxHalf: number) {
  return {
    maxFull: Math.floor(maxHalf / 2),
    maxHalf,
  };
}

export function getLengthError(
  t: TFunction,
  value: string | null | undefined,
  maxHalf: number,
  translationKey: string,
) {
  if (countFullWidthAndHalfWidthCharacters((value ?? "").trim()) <= maxHalf) {
    return "";
  }

  return t(translationKey, maxLengthParams(maxHalf));
}

export function getTagsError(t: TFunction, tags: string[]) {
  if (tags.length > maxKeywords) {
    return t("tooManyKeywords", { max: maxKeywords });
  }

  if (
    tags.some((tag) => countFullWidthAndHalfWidthCharacters(tag.trim()) > maxKeywordLengthInHalf)
  ) {
    return t("tooLongKeyword", maxLengthParams(maxKeywordLengthInHalf));
  }

  return "";
}
