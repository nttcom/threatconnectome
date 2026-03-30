import { NavigateFunction } from "react-router-dom";
import { preserveKeys } from "./const";

export const preserveParams = (currentParams: string) => {
  const newParams = new URLSearchParams();
  const currentUrlParams = new URLSearchParams(currentParams);

  // Retained Parameters Related to Toggle Buttons
  for (let key of preserveKeys) {
    const value = currentUrlParams.get(key);
    if (value !== null) {
      newParams.set(key, value);
    }
  }

  return newParams;
};

export const preserveMyTasksParam = (currentParams: string) => {
  const newParams = new URLSearchParams();
  const currentUrlParams = new URLSearchParams(currentParams);

  const value = currentUrlParams.get("mytasks");
  if (value !== null) {
    newParams.set("mytasks", value);
  }

  return newParams;
};

export const createUpdateParamsFunction = (location: Location, navigate: NavigateFunction) => {
  return (newParams: Record<string, string | number | null | undefined>) => {
    const updatedParams = new URLSearchParams(location.search);
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === null || value === undefined || value === "") {
        updatedParams.delete(key);
      } else {
        updatedParams.set(key, String(value));
      }
    });
    navigate(location.pathname + "?" + updatedParams.toString());
  };
};
