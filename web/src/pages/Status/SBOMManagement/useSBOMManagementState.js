import { useEffect, useMemo, useRef, useState } from "react";

import { NEW_SBOM_ID } from "../../../utils/SBOMManagement/sbomManagementUtils";

export function useSBOMManagementState({ initialActiveId, initialSboms }) {
  const [sboms, setSboms] = useState(initialSboms);
  const [activeId, setActiveId] = useState(initialActiveId ?? NEW_SBOM_ID);
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
    if (!isDirty) {
      setSboms(initialSboms);
    }
  }, [initialSboms, isDirty]);

  const resetUiState = () => {
    setIsDirty(false);
    setCurrentPage(1);
    setDangerOpen(false);
    setDeploymentsEditing(false);
    setDetailsEditing(false);
    setPendingThumbnail(null);
    setQuery("");
  };

  const lastInitialActiveIdRef = useRef(initialActiveId);
  useEffect(() => {
    if (initialActiveId === lastInitialActiveIdRef.current) return;
    lastInitialActiveIdRef.current = initialActiveId;
    setActiveId(initialActiveId ?? NEW_SBOM_ID);
    setIsDirty(false);
    setCurrentPage(1);
    setDangerOpen(false);
    setDeploymentsEditing(false);
    setDetailsEditing(false);
    setPendingThumbnail(null);
    setQuery("");
  }, [initialActiveId]);

  const isEmpty = sboms.length === 0;
  const isCreatingSbom = activeId === NEW_SBOM_ID || isEmpty;
  const activeSbom = useMemo(() => {
    if (isCreatingSbom) {
      return null;
    }

    return sboms.find((sbom) => sbom.id === activeId) || null;
  }, [activeId, isCreatingSbom, sboms]);

  const filteredDependencies = useMemo(() => {
    const target = query.trim().toLowerCase();

    if (!activeSbom) {
      return [];
    }

    if (!target) {
      return activeSbom.dependencies;
    }

    return activeSbom.dependencies.filter((dependency) =>
      dependency.name.toLowerCase().includes(target),
    );
  }, [activeSbom, query]);

  const totalPages = Math.max(1, Math.ceil(filteredDependencies.length / pageSize));
  const safeCurrentPage = Math.min(currentPage, totalPages);
  const pageStartIndex = (safeCurrentPage - 1) * pageSize;
  const pageEndIndex = Math.min(pageStartIndex + pageSize, filteredDependencies.length);
  const paginatedDependencies = filteredDependencies.slice(pageStartIndex, pageEndIndex);

  const updateActiveSbom = (patch) => {
    setIsDirty(true);
    setSboms((current) =>
      current.map((sbom) => (sbom.id === activeId ? { ...sbom, ...patch } : sbom)),
    );
  };

  const updateActiveSbomImage = (imageUrl) => {
    setSboms((current) =>
      current.map((sbom) => (sbom.id === activeSbom?.id ? { ...sbom, imageUrl } : sbom)),
    );
  };

  const addSbom = () => {
    setActiveId(NEW_SBOM_ID);
    setDeploymentsOpen(false);
    setDetailsOpen(false);
    resetUiState();
  };

  const cancelCreateSbom = () => {
    setActiveId(initialActiveId ?? NEW_SBOM_ID);
    resetUiState();
  };

  const selectSbom = (sbomId) => {
    setActiveId(sbomId);
    resetUiState();
  };

  return {
    activeId,
    activeSbom,
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
    sboms,
    selectSbom,
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
    updateActiveSbom,
    updateActiveSbomImage,
  };
}
