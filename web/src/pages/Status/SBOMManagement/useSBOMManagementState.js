import { useEffect, useMemo, useReducer, useRef, useState } from "react";

import { NEW_SBOM_ID } from "../../../utils/SBOMManagement/sbomManagementUtils";

function createEditorState(currentService) {
  return {
    activeServiceDraft: currentService,
    deploymentsEditing: false,
    detailsEditing: false,
    isDirty: false,
  };
}

function editorStateReducer(state, action) {
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
    case "resetDraftToCurrentService":
      return {
        ...state,
        activeServiceDraft: action.currentService,
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
  isThumbnailFetching = false,
  serviceTabs = [],
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
  const [pendingThumbnail, setPendingThumbnail] = useState(null);
  const [thumbnailDisplayOverride, setThumbnailDisplayOverride] = useState(null);
  const [awaitingThumbnailRefresh, setAwaitingThumbnailRefresh] = useState(false);
  const [hasSeenThumbnailRefetch, setHasSeenThumbnailRefetch] = useState(false);
  const [pendingUpload, setPendingUpload] = useState(null);
  const fileInputRef = useRef(null);
  const createFileInputRef = useRef(null);

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
    setThumbnailDisplayOverride(null);
    setAwaitingThumbnailRefresh(false);
    setHasSeenThumbnailRefetch(false);
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
    setThumbnailDisplayOverride(null);
    setAwaitingThumbnailRefresh(false);
    setHasSeenThumbnailRefetch(false);
    setQuery("");
  }, [currentService, selectedServiceId]);

  useEffect(() => {
    if (!awaitingThumbnailRefresh) {
      return;
    }

    if (isThumbnailFetching) {
      setHasSeenThumbnailRefetch(true);
      return;
    }

    if (!hasSeenThumbnailRefetch) {
      return;
    }

    setThumbnailDisplayOverride(null);
    setAwaitingThumbnailRefresh(false);
    setHasSeenThumbnailRefetch(false);
  }, [awaitingThumbnailRefresh, hasSeenThumbnailRefetch, isThumbnailFetching]);

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

  const updateActiveService = (patch) => {
    dispatchEditorState({ type: "updateActiveService", activeId, patch });
  };

  const resetDraftToCurrentService = () => {
    dispatchEditorState({ type: "resetDraftToCurrentService", currentService });
  };

  const setDetailsEditing = (value) => {
    dispatchEditorState({ type: "setDetailsEditing", value });
  };

  const setDeploymentsEditing = (value) => {
    dispatchEditorState({ type: "setDeploymentsEditing", value });
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

  const selectService = (serviceId) => {
    setActiveId(serviceId);
    resetUiState();
  };

  return {
    activeId,
    activeService,
    addSbom,
    cancelCreateSbom,
    createFileInputRef,
    currentPage,
    dangerOpen,
    deploymentsEditing: editorState.deploymentsEditing,
    deploymentsOpen,
    detailsEditing: editorState.detailsEditing,
    detailsOpen,
    fileInputRef,
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
    resetDraftToCurrentService,
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
    setThumbnailDisplayOverride,
    setAwaitingThumbnailRefresh,
    setPendingUpload,
    setQuery,
    totalPages,
    updateActiveService,
    thumbnailDisplayOverride,
  };
}
