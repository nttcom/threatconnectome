import { useSBOMManagementMutations } from "./useSBOMManagementMutations";
import { useSBOMManagementState } from "./useSBOMManagementState";

export function useSBOMManagementController({
  currentDependencies = [],
  currentService,
  isThumbnailFetching = false,
  onActiveIdChange,
  pteamId,
  serviceTabs = [],
}) {
  const state = useSBOMManagementState({
    currentDependencies,
    currentService,
    isThumbnailFetching,
    serviceTabs,
  });

  const mutations = useSBOMManagementMutations({
    actions: {
      markClean: state.markClean,
      resetUiState: state.resetUiState,
      setActiveId: state.setActiveId,
      setDeploymentsEditing: state.setDeploymentsEditing,
      setDetailsEditing: state.setDetailsEditing,
      setPendingThumbnail: state.setPendingThumbnail,
      setPendingUpload: state.setPendingUpload,
      setAwaitingThumbnailRefresh: state.setAwaitingThumbnailRefresh,
      setThumbnailDisplayOverride: state.setThumbnailDisplayOverride,
      updateActiveService: state.updateActiveService,
    },
    callbacks: {
      onActiveIdChange,
    },
    state: {
      activeId: state.activeId,
      activeService: state.activeService,
      isCreatingSbom: state.isCreatingSbom,
      pendingThumbnail: state.pendingThumbnail,
      pteamId,
      serviceTabs: state.serviceTabs,
      thumbnailDisplayOverride: state.thumbnailDisplayOverride,
    },
  });

  const displayedServiceTabs = state.serviceTabs.map((service) =>
    service.id === state.activeId && state.activeService
      ? { ...service, title: state.activeService.title }
      : service,
  );

  return {
    activeId: state.activeId,
    activeService: state.activeService,
    dependencies: {
      filtered: state.filteredDependencies,
      fileInputRef: state.fileInputRef,
      onFileUpload: mutations.handleFileUpload,
      pageEndIndex: state.pageEndIndex,
      pageSize: state.pageSize,
      pageStartIndex: state.pageStartIndex,
      paginated: state.paginatedDependencies,
      query: state.query,
      safeCurrentPage: state.safeCurrentPage,
      setCurrentPage: state.setCurrentPage,
      setPageSize: state.setPageSize,
      setQuery: state.setQuery,
      totalPages: state.totalPages,
    },
    deployments: {
      editing: state.deploymentsEditing,
      beginEditing: () => {
        state.setDeploymentsOpen(true);
        state.setDeploymentsEditing(true);
      },
      onAdd: mutations.addDeployment,
      onCommit: mutations.commitDeploymentsEdit,
      onRemove: mutations.removeDeployment,
      onToggle: () => state.setDeploymentsOpen((open) => !open),
      onUpdate: mutations.updateDeployment,
      open: state.deploymentsOpen,
    },
    details: {
      editing: state.detailsEditing,
      beginEditing: () => {
        state.setDetailsOpen(true);
        state.setDetailsEditing(true);
      },
      imageUrl: state.pendingThumbnail
        ? state.pendingThumbnail.previewDataUrl || ""
        : state.thumbnailDisplayOverride !== null
          ? state.thumbnailDisplayOverride
          : state.activeService?.imageUrl || "",
      onCommit: mutations.commitDetailsEdit,
      onImageUpload: mutations.handleImageUpload,
      onRemoveImage: mutations.handleRemoveImage,
      onToggle: () => state.setDetailsOpen((open) => !open),
      onUpdate: state.updateActiveService,
      open: state.detailsOpen,
    },
    dangerZone: {
      onDelete: mutations.removeActiveSbom,
      onToggle: () => state.setDangerOpen((open) => !open),
      open: state.dangerOpen,
    },
    isCreatingSbom: state.isCreatingSbom,
    isEmpty: state.isEmpty,
    newSbom: {
      inputRef: state.createFileInputRef,
      onCancel: state.cancelCreateSbom,
      onFileChange: mutations.handleCreateFileUpload,
    },
    pendingUpload: {
      existingServiceNames: state.pendingUpload?.serviceName
        ? undefined
        : state.serviceTabs.map((service) => service.title),
      onClose: () => state.setPendingUpload(null),
      onUploaded: () => state.setPendingUpload(null),
      value: state.pendingUpload,
    },
    riskSettings: {
      onSave: mutations.commitServiceImpactEdit,
    },
    tabs: {
      items: displayedServiceTabs,
      onAdd: state.addSbom,
      onSelect: (serviceId) => {
        state.selectService(serviceId);
        onActiveIdChange?.(serviceId);
      },
    },
  };
}
