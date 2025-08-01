import { preserveKeys } from "./const";

export const preserveParams = (currentParams) => {
  const newParams = new URLSearchParams();
  const currentUrlParams = new URLSearchParams(currentParams);

  // Retained Parameters Related to Toggle Buttons
  for (let key of preserveKeys) {
    if (currentUrlParams.has(key)) {
      newParams.set(key, currentUrlParams.get(key));
    }
  }

  return newParams;
};

export const preserveMyTasksParam = (currentParams) => {
  const newParams = new URLSearchParams();
  const currentUrlParams = new URLSearchParams(currentParams);

  if (currentUrlParams.has("mytasks")) {
    newParams.set("mytasks", currentUrlParams.get("mytasks"));
  }

  return newParams;
};

export const createUpdateParamsFunction = (location, navigate) => {
  return (newParams) => {
    const updatedParams = new URLSearchParams(location.search);
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === null || value === undefined || value === "") {
        updatedParams.delete(key);
      } else {
        updatedParams.set(key, value);
      }
    });
    navigate(location.pathname + "?" + updatedParams.toString());
  };
};
