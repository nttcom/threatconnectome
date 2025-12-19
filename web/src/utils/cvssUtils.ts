import { amber, grey, orange, red } from "@mui/material/colors";

export const cvssRatings = {
  None: { min: 0.0, max: 0.0 },
  Low: { min: 0.1, max: 3.9 },
  Medium: { min: 4.0, max: 6.9 },
  High: { min: 7.0, max: 8.9 },
  Critical: { min: 9.0, max: 10.0 },
};

export const cvssProps = {
  None: {
    cvssBgcolor: grey[600],
    threatCardBgcolor: grey[100],
  },
  Low: {
    cvssBgcolor: amber[600],
    threatCardBgcolor: amber[100],
  },
  Medium: {
    cvssBgcolor: amber[600],
    threatCardBgcolor: amber[100],
  },
  High: {
    cvssBgcolor: orange[600],
    threatCardBgcolor: orange[100],
  },
  Critical: {
    cvssBgcolor: red[600],
    threatCardBgcolor: red[100],
  },
};

export const getCvssColor = (score: number | null | undefined) => {
  if (score && score >= 9.0) return "error.main";
  if (score && score >= 7.0) return "warning.main";
  if (score && score >= 4.0) return "warning.light";
  if (!score) return "text.primary";
  return "success.main";
};

export const cvssConvertToName = (cvssScore: number) => {
  for (const [name, range] of Object.entries(cvssRatings)) {
    if (range.min <= cvssScore && cvssScore <= range.max) {
      return name;
    }
  }
  return "None";
};

type CVSSRatingName = "None" | "Low" | "Medium" | "High" | "Critical";

export const cvssConvertToScore = (cvssName: CVSSRatingName) => {
  const rating = cvssRatings[cvssName];
  if (rating) {
    return [rating.min, rating.max];
  }
  return [undefined, undefined];
};
