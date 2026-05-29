/* eslint-disable react/prop-types, jsx-a11y/no-autofocus */
import AddIcon from "@mui/icons-material/Add";
import { Box, Stack } from "@mui/material";
import { useTranslation } from "react-i18next";

import { SBOMUpdateDialog } from "../SbomDrop/SBOMUpdateDialog";
import { TabButton } from "./sharedUiParts";
import { DangerZone } from "./DangerZone";
import { DependenciesCard } from "./DependenciesCard";
import { DeploymentsPanel } from "./DeploymentsPanel";
import { DetailsPanel } from "./DetailsPanel";
import { NewSbomRegistrationPanel } from "./NewSbomRegistrationPanel";
import { RiskSettingsCard } from "./RiskSettingsCard";
import { slate } from "./styleTokens";
import { useSBOMManagementMutations } from "./useSBOMManagementMutations";
import { useSBOMManagementState } from "./useSBOMManagementState";

export function SBOMManagement({
  initialActiveId,
  initialSboms = [],
  onActiveIdChange,
  onThumbnailChange,
  onPackageClick,
  pteamId,
}) {
  const { t } = useTranslation("status", { keyPrefix: "SBOMManagement" });
  const {
    activeId,
    activeSbom,
    addSbom,
    cancelCreateSbom,
    createFileInputRef,
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
  } = useSBOMManagementState({ initialActiveId, initialSboms });

  const {
    addDeployment,
    commitDeploymentsEdit,
    commitDetailsEdit,
    commitServiceImpactEdit,
    handleCreateFileUpload,
    handleFileUpload,
    handleImageUpload,
    handleRemoveImage,
    removeActiveSbom,
    removeDeployment,
    updateDeployment,
  } = useSBOMManagementMutations({
    activeId,
    activeSbom,
    isCreatingSbom,
    onActiveIdChange,
    onThumbnailChange,
    pteamId,
    resetUiState,
    sboms,
    setActiveId,
    setDeploymentsEditing,
    setDetailsEditing,
    setPendingThumbnail,
    setPendingUpload,
    updateActiveSbom,
    updateActiveSbomImage,
  });

  if (!activeSbom && !isCreatingSbom) {
    return null;
  }

  return (
    <Box
      sx={{
        bgcolor: slate[100],
        color: slate[950],
        minHeight: "100vh",
        overflowX: "hidden",
        p: { sm: 3, xs: 1.5 },
      }}
    >
      <Box sx={{ maxWidth: 1600, minWidth: 0, mx: "auto", width: "100%" }}>
        <Stack
          direction="row"
          alignItems="flex-end"
          sx={{
            borderBottom: `1px solid ${slate[200]}`,
            gap: 1,
            minWidth: 0,
            overflowX: "auto",
            px: 0.5,
            width: "100%",
          }}
        >
          {sboms.map((sbom) => (
            <TabButton
              active={sbom.id === activeId}
              key={sbom.id}
              onClick={() => {
                selectSbom(sbom.id);
                onActiveIdChange?.(sbom.id);
              }}
              sbom={sbom}
            />
          ))}
          <Box
            component="button"
            onClick={addSbom}
            sx={{
              "&:hover": { bgcolor: "white", borderColor: slate[400], color: slate[900] },
              alignItems: "center",
              bgcolor: isCreatingSbom ? "white" : slate[50],
              border: "1px solid",
              borderColor: isCreatingSbom ? slate[200] : slate[300],
              borderStyle: isCreatingSbom ? "solid" : "dashed",
              borderTopLeftRadius: 16,
              borderTopRightRadius: 16,
              boxShadow: isCreatingSbom ? "0 1px 2px rgba(15, 23, 42, 0.05)" : "none",
              color: isCreatingSbom ? slate[950] : slate[500],
              cursor: "pointer",
              display: "flex",
              font: "inherit",
              fontSize: 14,
              fontWeight: 600,
              gap: 1,
              ml: 0.5,
              px: 2.5,
              py: 1.5,
              transition: "background-color 160ms ease, color 160ms ease, border-color 160ms ease",
              whiteSpace: "nowrap",
            }}
            type="button"
          >
            <AddIcon sx={{ fontSize: 18 }} />
            {t("addNew")}
          </Box>
        </Stack>

        {isCreatingSbom ? (
          <NewSbomRegistrationPanel
            inputRef={createFileInputRef}
            onCancel={cancelCreateSbom}
            onFileChange={handleCreateFileUpload}
            showCancel={!isEmpty}
          />
        ) : (
          <Box
            sx={{
              bgcolor: "white",
              borderBottomLeftRadius: 24,
              borderBottomRightRadius: 24,
              borderTopRightRadius: 24,
              boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
              display: "grid",
              gap: 3,
              gridTemplateColumns: {
                lg: "minmax(280px, 0.7fr) minmax(0, 1.9fr)",
                xl: "minmax(320px, 0.75fr) minmax(0, 2.35fr)",
                xs: "1fr",
              },
              minWidth: 0,
              p: { sm: 2.5, xs: 1.5 },
              width: "100%",
            }}
          >
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1, minWidth: 0 }}>
              <DetailsPanel
                editing={detailsEditing}
                imageUrl={
                  pendingThumbnail ? pendingThumbnail.previewDataUrl || "" : activeSbom.imageUrl
                }
                onCommit={() => {
                  if (detailsEditing) {
                    commitDetailsEdit(pendingThumbnail);
                  } else {
                    setDetailsOpen(true);
                    setDetailsEditing(true);
                  }
                }}
                onImageUpload={handleImageUpload}
                onRemoveImage={handleRemoveImage}
                onToggle={() => setDetailsOpen((open) => !open)}
                onUpdate={updateActiveSbom}
                open={detailsOpen}
                sbom={activeSbom}
              />

              <RiskSettingsCard onSave={commitServiceImpactEdit} sbom={activeSbom} />

              <DeploymentsPanel
                deployments={activeSbom.deployments}
                editing={deploymentsEditing}
                onAdd={addDeployment}
                onCommit={() => {
                  if (deploymentsEditing) {
                    commitDeploymentsEdit();
                  } else {
                    setDeploymentsOpen(true);
                    setDeploymentsEditing(true);
                  }
                }}
                onRemove={removeDeployment}
                onToggle={() => setDeploymentsOpen((open) => !open)}
                onUpdate={updateDeployment}
                open={deploymentsOpen}
              />

              <DangerZone
                onDelete={removeActiveSbom}
                onToggle={() => setDangerOpen((open) => !open)}
                open={dangerOpen}
                sbomTitle={activeSbom.title}
              />
            </Box>

            <DependenciesCard
              filteredDependencies={filteredDependencies}
              fileInputRef={fileInputRef}
              onFileUpload={handleFileUpload}
              onPackageClick={onPackageClick}
              pageEndIndex={pageEndIndex}
              pageSize={pageSize}
              pageStartIndex={pageStartIndex}
              paginatedDependencies={paginatedDependencies}
              query={query}
              safeCurrentPage={safeCurrentPage}
              setCurrentPage={setCurrentPage}
              setPageSize={setPageSize}
              setQuery={setQuery}
              totalPages={totalPages}
            />
          </Box>
        )}
      </Box>
      <SBOMUpdateDialog
        open={!!pendingUpload}
        onClose={() => setPendingUpload(null)}
        pteamId={pteamId}
        initialFile={pendingUpload?.file ?? null}
        serviceName={pendingUpload?.serviceName}
        existingServiceNames={
          pendingUpload && !pendingUpload.serviceName ? sboms.map((sbom) => sbom.title) : undefined
        }
        showWarning={!!pendingUpload?.serviceName}
        onUploaded={() => setPendingUpload(null)}
      />
    </Box>
  );
}

export default SBOMManagement;
