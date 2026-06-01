import { useEffect, useMemo, useRef, useState } from "react";

import { NEW_SBOM_ID } from "../../../utils/SBOMManagement/sbomManagementUtils";

export function useSBOMManagementState({
  currentDependencies = [],
  currentService,
  serviceTabs = [],
}) {
  const selectedServiceId = currentService?.id ?? null;
  const [activeId, setActiveId] = useState(selectedServiceId ?? NEW_SBOM_ID);
  const [activeServiceDraft, setActiveServiceDraft] = useState(currentService);
  const [isDirty, setIsDirty] = useState(false);
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [detailsEditing, setDetailsEditing] = useState(false);
  const [deploymentsOpen, setDeploymentsOpen] = useState(false);
  const [deploymentsEditing, setDeploymentsEditing] = useState(false);
  const [dangerOpen, setDangerOpen] = useState(false);
  const [pendingThumbnail, setPendingThumbnail] = useState(null);
  const [pendingUpload, setPendingUpload] = useState(null);
  const fileInputRef = useRef(null);
  const createFileInputRef = useRef(null);

  useEffect(() => {
    if (!serviceTabs.length) {
      setActiveId(NEW_SBOM_ID);
    }
  }, [serviceTabs.length]);

  useEffect(() => {
    if (!isDirty) {
      setActiveServiceDraft(currentService);
    }
  }, [currentService, isDirty]);

  const resetUiState = () => {
    setIsDirty(false);
    setCurrentPage(1);
    setDangerOpen(false);
    setDeploymentsEditing(false);
    setDetailsEditing(false);
    setPendingThumbnail(null);
    setQuery("");
  };

  const lastSelectedServiceIdRef = useRef(selectedServiceId);
  useEffect(() => {
    if (selectedServiceId === lastSelectedServiceIdRef.current) return;
    lastSelectedServiceIdRef.current = selectedServiceId;
    setActiveId(selectedServiceId ?? NEW_SBOM_ID);
    setActiveServiceDraft(currentService);
    setIsDirty(false);
    setCurrentPage(1);
    setDangerOpen(false);
    setDeploymentsEditing(false);
    setDetailsEditing(false);
    setPendingThumbnail(null);
    setQuery("");
  }, [currentService, selectedServiceId]);

  const isEmpty = serviceTabs.length === 0;
  const isCreatingSbom = activeId === NEW_SBOM_ID || isEmpty;
  const activeService = useMemo(() => {
    if (isCreatingSbom) {
      return null;
    }

    if (activeServiceDraft?.id !== activeId) {
      return null;
    }

    return activeServiceDraft;
  }, [activeId, activeServiceDraft, isCreatingSbom]);

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
    setIsDirty(true);
    setActiveServiceDraft((current) =>
      current?.id === activeId ? { ...current, ...patch } : current,
    );
  };

  const markClean = () => {
    setIsDirty(false);
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
    deploymentsEditing,
    deploymentsOpen,
    detailsEditing,
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
    totalPages,
    markClean,
    updateActiveService,
  };
}
