import type { ChangeEvent } from "react";
import type { TodoApiParams, SortConfig, UseTodoStateReturn } from "../../hooks/ToDo/useTodoState";

export type TodoViewProps = {
  pteamIds: string[];
  apiParams: TodoApiParams;
  onMyTasksChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onCveSearch: (word: string) => void;
  onSortConfigChange: (newConfig: SortConfig) => void;
  onItemsPerPageChange: (newValue: number) => void;
  onPageChange: UseTodoStateReturn["onPageChange"];
};
