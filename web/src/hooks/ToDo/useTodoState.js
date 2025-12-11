import { useMemo, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export const useTodoState = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const params = useMemo(() => new URLSearchParams(location.search), [location.search]);

  const myTasks = params.get("mytasks") === "on" || !params.has("mytasks");
  const cveId = params.get("cve_id")?.trim() ?? "";
  const page = parseInt(params.get("page"), 10) || 1;
  const itemsPerPage = parseInt(params.get("perPage"), 10) || 10;
  const sortConfig = useMemo(
    () => ({
      key: params.get("sortKey") || "ssvc_deployer_priority",
      direction: params.get("sortDirection") || "desc",
    }),
    [params],
  );

  const updateParams = useCallback(
    (newValues) => {
      const newParams = new URLSearchParams(location.search);
      Object.entries(newValues).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== "") {
          newParams.set(key, value);
        } else {
          newParams.delete(key);
        }
      });

      // IMPORTANT: When sorting or filtering, reset to page 1 by deleting the 'page' parameter.
      // This causes the `page` variable to default to 1 on the next render.
      if (!("page" in newValues)) {
        newParams.delete("page");
      }
      navigate({ search: newParams.toString() });
    },
    [location.search, navigate],
  );

  const onMyTasksChange = useCallback(
    (event) => updateParams({ mytasks: event.target.checked ? "on" : "off" }),
    [updateParams],
  );

  const onCveSearch = useCallback((word) => updateParams({ cve_id: word }), [updateParams]);

  const onSortConfigChange = useCallback(
    (newConfig) => updateParams({ sortKey: newConfig.key, sortDirection: newConfig.direction }),
    [updateParams],
  );

  const onItemsPerPageChange = useCallback(
    (newValue) => updateParams({ perPage: newValue }),
    [updateParams],
  );

  const onPageChange = useCallback(
    (event, newPage) => updateParams({ page: newPage }),
    [updateParams],
  );

  const apiParams = useMemo(
    () => ({
      page,
      sortConfig,
      offset: (page - 1) * itemsPerPage,
      limit: itemsPerPage,
      sort_keys: [
        sortConfig.direction === "asc" ? sortConfig.key : `-${sortConfig.key}`,
        "-created_at",
      ],
      assigned_to_me: myTasks,
      exclude_statuses: ["completed"],
      cve_ids: cveId ? [cveId] : [],
    }),
    [page, itemsPerPage, sortConfig, myTasks, cveId],
  );

  return {
    apiParams,
    onMyTasksChange,
    onCveSearch,
    onSortConfigChange,
    onItemsPerPageChange,
    onPageChange,
  };
};
