import type { ChangeEvent } from "react";
import { useMemo, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export type SortConfig = {
  key: string;
  direction: string;
};

export type TodoApiParams = {
  page: number;
  sortConfig: SortConfig;
  offset: number;
  limit: number;
  sort_keys: string[];
  assigned_to_me: boolean;
  exclude_statuses: string[];
  cve_ids: string[];
};

type UpdateParamValue = string | number | null | undefined;

export type UseTodoStateReturn = {
  apiParams: TodoApiParams;
  onMyTasksChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onCveSearch: (word: string) => void;
  onSortConfigChange: (newConfig: SortConfig) => void;
  onItemsPerPageChange: (newValue: number) => void;
  onPageChange: (event: unknown, newPage: number) => void;
};

export const useTodoState = (): UseTodoStateReturn => {
  const location = useLocation();
  const navigate = useNavigate();
  const params = useMemo(() => new URLSearchParams(location.search), [location.search]);

  const myTasks = params.get("mytasks") === "on" || !params.has("mytasks");
  const cveId = params.get("cve_id")?.trim() ?? "";
  const page = parseInt(params.get("page") ?? "", 10) || 1;
  const itemsPerPage = parseInt(params.get("perPage") ?? "", 10) || 10;
  const sortConfig = useMemo<SortConfig>(
    () => ({
      key: params.get("sortKey") || "ssvc_deployer_priority",
      direction: params.get("sortDirection") || "desc",
    }),
    [params],
  );

  const updateParams = useCallback(
    (newValues: Record<string, UpdateParamValue>) => {
      const newParams = new URLSearchParams(location.search);
      Object.entries(newValues).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== "") {
          newParams.set(key, String(value));
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
    (event: ChangeEvent<HTMLInputElement>) =>
      updateParams({ mytasks: event.target.checked ? "on" : "off" }),
    [updateParams],
  );

  const onCveSearch = useCallback((word: string) => updateParams({ cve_id: word }), [updateParams]);

  const onSortConfigChange = useCallback(
    (newConfig: SortConfig) =>
      updateParams({ sortKey: newConfig.key, sortDirection: newConfig.direction }),
    [updateParams],
  );

  const onItemsPerPageChange = useCallback(
    (newValue: number) => updateParams({ perPage: newValue }),
    [updateParams],
  );

  const onPageChange = useCallback(
    (event: unknown, newPage: number) => {
      void event;
      updateParams({ page: newPage });
    },
    [updateParams],
  );

  const apiParams = useMemo<TodoApiParams>(
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
