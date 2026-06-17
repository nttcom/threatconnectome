/* eslint-disable react/prop-types */
import AddIcon from "@mui/icons-material/Add";
import { Box, Stack } from "@mui/material";
import { useTranslation } from "react-i18next";

import { SBOMUpdateDialog } from "../SbomDrop/SBOMUpdateDialog";

import { DangerZone } from "./DangerZone";
import { DependenciesCard } from "./DependenciesCard";
import { DeploymentsPanel } from "./DeploymentsPanel";
import { DetailsPanel } from "./DetailsPanel";
import { NewSbomRegistrationPanel } from "./NewSbomRegistrationPanel";
import { RiskSettingsCard } from "./RiskSettingsCard";
import { TabButton } from "./sharedUiParts";
import { slate, tabButtonSx, tabPanelSx, uiRadii } from "./styleTokens";
import { useSBOMManagementController } from "./useSBOMManagementController";

export function SBOMManagement({
  currentDependencies = [],
  currentService,
  onActiveIdChange,
  onPackageClick,
  pteamId,
  serviceTabs = [],
}) {
  const { t } = useTranslation("status", { keyPrefix: "SBOMManagement" });
  const {
    activeId,
    activeService,
    dangerZone,
    dependencies,
    deployments,
    details,
    isCreatingSbom,
    isEmpty,
    newSbom,
    pendingUpload,
    riskSettings,
    tabs,
  } = useSBOMManagementController({
    currentDependencies,
    currentService,
    onActiveIdChange,
    pteamId,
    serviceTabs,
  });
  const isActiveServicePending = !activeService && !isCreatingSbom;

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
          {tabs.items.map((service) => (
            <TabButton
              active={service.id === activeId}
              key={service.id}
              onClick={() => tabs.onSelect(service.id)}
              sbom={service}
            />
          ))}
          <Box
            component="button"
            onClick={tabs.onAdd}
            sx={{
              "&:hover": { bgcolor: "white", borderColor: slate[400], color: slate[900] },
              alignItems: "center",
              bgcolor: isCreatingSbom ? "white" : slate[50],
              border: "1px solid",
              borderColor: isCreatingSbom ? slate[200] : slate[300],
              borderStyle: isCreatingSbom ? "solid" : "dashed",
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
              ...tabButtonSx,
              boxShadow: isCreatingSbom ? tabButtonSx.boxShadow : "none",
            }}
            type="button"
          >
            <AddIcon sx={{ fontSize: 18 }} />
            {t("addNew")}
          </Box>
        </Stack>

        {isCreatingSbom ? (
          <NewSbomRegistrationPanel
            onCancel={newSbom.onCancel}
            onDropFile={pendingUpload.onCreateWithFile}
            onUploadClick={newSbom.onUploadClick}
            showCancel={!isEmpty}
          />
        ) : isActiveServicePending ? (
          <Box
            sx={{
              ...tabPanelSx,
              p: { sm: 2.5, xs: 1.5 },
            }}
          >
            <Box
              sx={{
                alignItems: "center",
                border: `1px solid ${slate[200]}`,
                borderRadius: uiRadii.statusCard,
                color: slate[500],
                display: "flex",
                fontSize: 14,
                justifyContent: "center",
                minHeight: 240,
                px: 2,
                textAlign: "center",
              }}
            >
              {t("loadingSelectedSbom")}
            </Box>
          </Box>
        ) : (
          <Box
            sx={{
              ...tabPanelSx,
              display: "grid",
              gap: 3,
              gridTemplateColumns: {
                lg: "minmax(280px, 0.7fr) minmax(0, 1.9fr)",
                xl: "minmax(320px, 0.75fr) minmax(0, 2.35fr)",
                xs: "1fr",
              },
              p: { sm: 2.5, xs: 1.5 },
            }}
          >
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1, minWidth: 0 }}>
              <DetailsPanel
                editing={details.editing}
                imageUrl={details.imageUrl}
                onCommit={() => {
                  if (details.editing) {
                    details.onCommit();
                  } else {
                    details.beginEditing();
                  }
                }}
                onImageUpload={details.onImageUpload}
                onRemoveImage={details.onRemoveImage}
                onToggle={details.onToggle}
                onUpdate={details.onUpdate}
                open={details.open}
                sbom={activeService}
              />

              <RiskSettingsCard onSave={riskSettings.onSave} sbom={activeService} />

              <DeploymentsPanel
                deployments={activeService.deployments}
                editing={deployments.editing}
                onAdd={deployments.onAdd}
                onCommit={() => {
                  if (deployments.editing) {
                    deployments.onCommit();
                  } else {
                    deployments.beginEditing();
                  }
                }}
                onRemove={deployments.onRemove}
                onToggle={deployments.onToggle}
                onUpdate={deployments.onUpdate}
                open={deployments.open}
              />

              <DangerZone
                onDelete={dangerZone.onDelete}
                onToggle={dangerZone.onToggle}
                open={dangerZone.open}
                sbomTitle={activeService.title}
              />
            </Box>

            <DependenciesCard
              filteredDependencies={dependencies.filtered}
              onUpdateClick={dependencies.onUpdateClick}
              onPackageClick={onPackageClick}
              pageEndIndex={dependencies.pageEndIndex}
              pageSize={dependencies.pageSize}
              pageStartIndex={dependencies.pageStartIndex}
              paginatedDependencies={dependencies.paginated}
              query={dependencies.query}
              safeCurrentPage={dependencies.safeCurrentPage}
              setCurrentPage={dependencies.setCurrentPage}
              setPageSize={dependencies.setPageSize}
              setQuery={dependencies.setQuery}
              totalPages={dependencies.totalPages}
            />
          </Box>
        )}
      </Box>
      <SBOMUpdateDialog
        initialFile={pendingUpload.value?.initialFile}
        open={!!pendingUpload.value}
        onClose={pendingUpload.onClose}
        pteamId={pteamId}
        serviceName={pendingUpload.value?.serviceName}
        existingServiceNames={pendingUpload.existingServiceNames}
        showWarning={!!pendingUpload.value?.serviceName}
        onUploaded={pendingUpload.onUploaded}
      />
    </Box>
  );
}

export default SBOMManagement;
