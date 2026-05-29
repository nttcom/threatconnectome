import { maxKeywordLengthInHalf, maxKeywords } from "../const";
import { countFullWidthAndHalfWidthCharacters } from "../func";

function maxLengthParams(maxHalf) {
  return {
    maxFull: Math.floor(maxHalf / 2),
    maxHalf,
  };
}

export function getLengthError(t, value, maxHalf, translationKey) {
  if (countFullWidthAndHalfWidthCharacters((value ?? "").trim()) <= maxHalf) {
    return "";
  }

  return t(translationKey, maxLengthParams(maxHalf));
}

export function getTagsError(t, tags) {
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
