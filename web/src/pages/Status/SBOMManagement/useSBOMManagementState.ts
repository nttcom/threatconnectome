import { useEffect, useMemo, useReducer, useRef, useState } from "react";

import { NEW_SBOM_ID } from "../../../utils/SBOMManagement/sbomManagementUtils";

import type {
  PendingThumbnail,
  PendingUpload,
  SbomDependency,
  SbomService,
  SbomServicePatch,
  SbomServiceTab,
} from "./SBOMManagementTypes";

type EditorState = {
  activeServiceDraft: SbomService | null;
  deploymentsEditing: boolean;
  detailsEditing: boolean;
  isDirty: boolean;
};

type EditorAction =
  | { type: "syncCurrentService"; currentService: SbomService | null }
  | { type: "replaceCurrentService"; currentService: SbomService | null }
  | { type: "resetUi" }
  | { type: "updateActiveService"; activeId: string; patch: SbomServicePatch }
  | { type: "markClean" }
  | { type: "setDetailsEditing"; value: boolean }
  | { type: "setDeploymentsEditing"; value: boolean };

function createEditorState(currentService: SbomService | null): EditorState {
  return {
    activeServiceDraft: currentService,
    deploymentsEditing: false,
    detailsEditing: false,
    isDirty: false,
  };
}

function editorStateReducer(state: EditorState, action: EditorAction): EditorState {
  switch (action.type) {
    case "syncCurrentService":
      return {
        ...state,
        activeServiceDraft: action.currentService,
      };
    case "replaceCurrentService":
      return createEditorState(action.currentService);
    case "resetUi":
      return {
        ...state,
        deploymentsEditing: false,
        detailsEditing: false,
        isDirty: false,
      };
    case "updateActiveService":
      return {
        ...state,
        activeServiceDraft:
          state.activeServiceDraft?.id === action.activeId
            ? { ...state.activeServiceDraft, ...action.patch }
            : state.activeServiceDraft,
        isDirty: true,
      };
    case "markClean":
      return {
        ...state,
        isDirty: false,
      };
    case "setDetailsEditing":
      return {
        ...state,
        detailsEditing: action.value,
      };
    case "setDeploymentsEditing":
      return {
        ...state,
        deploymentsEditing: action.value,
      };
    default:
      return state;
  }
}

export function useSBOMManagementState({
  currentDependencies = [],
  currentService,
  serviceTabs = [],
}: {
  currentDependencies?: SbomDependency[];
  currentService: SbomService | null;
  serviceTabs?: SbomServiceTab[];
}) {
  const selectedServiceId = currentService?.id ?? null;
  const [activeId, setActiveId] = useState(selectedServiceId ?? NEW_SBOM_ID);
  const [editorState, dispatchEditorState] = useReducer(
    editorStateReducer,
    currentService,
    createEditorState,
  );
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [deploymentsOpen, setDeploymentsOpen] = useState(false);
  const [dangerOpen, setDangerOpen] = useState(false);
  const [pendingThumbnail, setPendingThumbnail] = useState<PendingThumbnail | null>(null);
  const [pendingUpload, setPendingUpload] = useState<PendingUpload | null>(null);

  useEffect(() => {
    if (!serviceTabs.length) {
      setActiveId(NEW_SBOM_ID);
    }
  }, [serviceTabs.length]);

  useEffect(() => {
    if (!editorState.isDirty) {
      dispatchEditorState({ type: "syncCurrentService", currentService });
    }
  }, [currentService, editorState.isDirty]);

  const resetUiState = () => {
    dispatchEditorState({ type: "resetUi" });
    setCurrentPage(1);
    setDangerOpen(false);
    setPendingThumbnail(null);
    setQuery("");
  };

  const lastSelectedServiceIdRef = useRef(selectedServiceId);
  useEffect(() => {
    if (selectedServiceId === lastSelectedServiceIdRef.current) return;
    lastSelectedServiceIdRef.current = selectedServiceId;
    setActiveId(selectedServiceId ?? NEW_SBOM_ID);
    dispatchEditorState({ type: "replaceCurrentService", currentService });
    setCurrentPage(1);
    setDangerOpen(false);
    setPendingThumbnail(null);
    setQuery("");
  }, [currentService, selectedServiceId]);

  const isEmpty = serviceTabs.length === 0;
  const isCreatingSbom = activeId === NEW_SBOM_ID || isEmpty;
  const activeService = useMemo(() => {
    if (isCreatingSbom) {
      return null;
    }

    if (editorState.activeServiceDraft?.id !== activeId) {
      return null;
    }

    return editorState.activeServiceDraft;
  }, [activeId, editorState.activeServiceDraft, isCreatingSbom]);

  const filteredDependencies = useMemo(() => {
    const target = query.trim().toLowerCase();

    if (!activeService) {
      return [];
    }

    if (!target) {
      return currentDependencies;
    }

    return currentDependencies.filter((dependency) =>
      dependency.name.toLowerCase().includes(target),
    );
  }, [activeService, currentDependencies, query]);

  const totalPages = Math.max(1, Math.ceil(filteredDependencies.length / pageSize));
  const safeCurrentPage = Math.min(currentPage, totalPages);
  const pageStartIndex = (safeCurrentPage - 1) * pageSize;
  const pageEndIndex = Math.min(pageStartIndex + pageSize, filteredDependencies.length);
  const paginatedDependencies = filteredDependencies.slice(pageStartIndex, pageEndIndex);

  const updateActiveService = (patch: SbomServicePatch) => {
    dispatchEditorState({ type: "updateActiveService", activeId, patch });
  };

  const setDetailsEditing = (value: boolean) => {
    dispatchEditorState({ type: "setDetailsEditing", value });
  };

  const setDeploymentsEditing = (value: boolean) => {
    dispatchEditorState({ type: "setDeploymentsEditing", value });
  };

  const markClean = () => {
    dispatchEditorState({ type: "markClean" });
  };

  const addSbom = () => {
    setActiveId(NEW_SBOM_ID);
    setDeploymentsOpen(false);
    setDetailsOpen(false);
    resetUiState();
  };

  const cancelCreateSbom = () => {
    setActiveId(selectedServiceId ?? NEW_SBOM_ID);
    resetUiState();
  };

  const selectService = (serviceId: string) => {
    setActiveId(serviceId);
    resetUiState();
  };

  return {
    activeId,
    activeService,
    addSbom,
    cancelCreateSbom,
    currentPage,
    dangerOpen,
    deploymentsEditing: editorState.deploymentsEditing,
    deploymentsOpen,
    detailsEditing: editorState.detailsEditing,
    detailsOpen,
    filteredDependencies,
    isCreatingSbom,
    isEmpty,
    pageEndIndex,
    pageSize,
    pageStartIndex,
    paginatedDependencies,
    pendingThumbnail,
    pendingUpload,
    query,
    resetUiState,
    safeCurrentPage,
    selectService,
    serviceTabs,
    setActiveId,
    setCurrentPage,
    setDangerOpen,
    setDeploymentsEditing,
    setDeploymentsOpen,
    setDetailsEditing,
    setDetailsOpen,
    setPageSize,
    setPendingThumbnail,
    setPendingUpload,
    setQuery,
    markClean,
    totalPages,
    updateActiveService,
  };
}
