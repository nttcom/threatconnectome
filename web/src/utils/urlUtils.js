import { preserveKeys } from "./const";

export const preserveParams = (currentParams) => {
  const newParams = new URLSearchParams();
  const currentUrlParams = new URLSearchParams(currentParams);
  console.log("Current URL Params:", currentUrlParams.toString());

  // Retained Parameters Related to Toggle Buttons
  for (let key of preserveKeys) {
    if (currentUrlParams.has(key)) {
      newParams.set(key, currentUrlParams.get(key));
    }
  }

  return newParams;
};
