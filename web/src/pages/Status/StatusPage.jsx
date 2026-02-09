import {
  AddCircleOutlineRounded as AddCircleOutlineRoundedIcon,
  Check as CheckIcon,
  Clear as ClearIcon,
  RemoveCircleOutline as RemoveCircleOutlineIcon,
} from "@mui/icons-material";
import {
  Box,
  Chip,
  FormControlLabel,
  IconButton,
  InputAdornment,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  MenuList,
  Pagination,
  Paper,
  Select,
  Table,
  TableBody,
  TableContainer,
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";

import { Android12Switch } from "../../components/Android12Switch";
import { PTeamLabel } from "../../components/PTeamLabel";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetPTeamQuery, useGetPTeamPackagesSummaryQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { getNoPTeamMessage } from "../../utils/const";
import { errorToString } from "../../utils/func";
import { sortedSSVCPriorities, getSsvcPriorityProps } from "../../utils/ssvcUtils";
import { preserveMyTasksParam, preserveParams } from "../../utils/urlUtils";

import { DeleteServiceIcon } from "./DeleteServiceIcon";
import { PTeamServiceDetailsResponsive } from "./PTeamServiceDetails/PTeamServiceDetailsResponsive";
import { PTeamServiceSelectDialog } from "./PTeamServiceSelectDialog";
import { PTeamServiceTabs } from "./PTeamServiceTabs";
import { PTeamServicesListModal } from "./PTeamServicesListModal";
import { PTeamStatusCard } from "./PTeamStatusCard";
import { PTeamStatusCardFallback } from "./PTeamStatusCardFallback";
import { SBOMDropArea } from "./SBOMDropArea";

const ssvcPriorityCountMax = 99999;

function SearchField(props) {
  const { word, onApply } = props;
  const [newWord, setNewWord] = useState(word);
  const { t } = useTranslation("status", { keyPrefix: "StatusPage" });

  return (
    <>
      <TextField
        variant="standard"
        label={word === newWord ? t("search") : t("search_enter")}
        size="small"
        value={newWord}
        onChange={(event) => setNewWord(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            onApply(event.target.value);
          }
        }}
        sx={{ textTransform: "none", width: { md: "290px", xs: "100%" } }}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={() => {
                  setNewWord("");
                  onApply("");
                }}
                size="small"
              >
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
    </>
  );
}

SearchField.propTypes = {
  word: PropTypes.string.isRequired,
  onApply: PropTypes.func.isRequired,
};

function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

CustomTabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

export function Status() {
  const location = useLocation();
  const navigate = useNavigate();

  const params = new URLSearchParams(location.search);
  const searchWord = params.get("word")?.trim().toLowerCase() ?? "";

  const pteamId = params.get("pteamId");
  const serviceId = params.get("serviceId");

  const [expandService, setExpandService] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const searchMenuOpen = Boolean(anchorEl);

  const isActiveAllServicesMode = params.get("allservices") === "on" ? true : false;
  const [isActiveUploadMode, setIsActiveUploadMode] = useState(0);

  const [pTeamServicesListModalOpen, setPTeamServicesListModalOpen] = useState(false);
  const [selectedPackageInfo, setSelectedPackageInfo] = useState({
    packageId: "",
    packageName: "",
    serviceIds: [],
  });

  const skipByAuth = useSkipUntilAuthUserIsReady();

  const {
    data: pteam,
    error: pteamError,
    isFetching: pteamIsFetching,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery({ path: { pteam_id: pteamId } }, { skip: skipByAuth || !pteamId });

  const {
    currentData: pteamAllServicesPackagesSummary,
    error: pteamAllServicesPackagesSummaryError,
    isFetching: pteamAllServicesPackagesSummaryIsFetching,
  } = useGetPTeamPackagesSummaryQuery(
    { path: { pteam_id: pteamId } },
    {
      skip: skipByAuth || !pteamId || !isActiveAllServicesMode,
    },
  );

  const {
    currentData: pteamServicePackagesSummary,
    error: pteamServicePackagesSummaryError,
    isFetching: pteamServicePackagesSummaryIsFetching,
  } = useGetPTeamPackagesSummaryQuery(
    { path: { pteam_id: pteamId }, query: { service_id: serviceId } },
    {
      skip: skipByAuth || !pteamId || !serviceId || isActiveAllServicesMode,
    },
  );

  useEffect(() => {
    if (!pteamId) return; // wait fixed by App
    if (pteamIsFetching || !pteam) return; // wait getQuery

    if (!serviceId) {
      if (pteam.services.length === 0) return; // nothing to do any more.
      // no service selected. force selecting one of services -- the first one
      const newParams = new URLSearchParams();
      newParams.set("pteamId", pteamId);
      newParams.set("serviceId", pteam.services[0].service_id);

      const MytasksParam = preserveMyTasksParam(location.search);
      for (const [key, value] of MytasksParam) {
        newParams.set(key, value);
      }
      navigate(location.pathname + "?" + newParams.toString());
      return;
    }

    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [pteamId, pteam, serviceId, isActiveAllServicesMode]);

  useEffect(() => {
    setIsActiveUploadMode(0); // reset upload mode
  }, [pteamId]);

  const handleServiceDeleted = () => {
    // If upload mode is active when service deletion occurs, disable upload mode
    if (isActiveUploadMode === 1) {
      setIsActiveUploadMode(0);
    }
  };

  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));
  const isSmDown = useMediaQuery(theme.breakpoints.down("sm"));
  const { t } = useTranslation("status", { keyPrefix: "StatusPage" });

  if (!pteamId) return <>{getNoPTeamMessage()}</>;
  if (skipByAuth || !pteamId) return <></>;
  if (pteamError)
    throw new APIError(errorToString(pteamError), {
      api: "getPTeam",
    });
  if (pteamIsLoading) return <>{t("loading_team")}</>;

  if (pteamAllServicesPackagesSummaryError)
    throw new APIError(errorToString(pteamAllServicesPackagesSummaryError), {
      api: "getPTeamPackagesSummary",
    });

  if (pteamServicePackagesSummaryError)
    throw new APIError(errorToString(pteamServicePackagesSummaryError), {
      api: "getPTeamPackagesSummary",
    });

  if (
    (!pteamAllServicesPackagesSummary && isActiveAllServicesMode) ||
    (!pteamServicePackagesSummary &&
      !isActiveAllServicesMode &&
      (serviceId || pteam.services.length > 0)) ||
    (pteamAllServicesPackagesSummaryIsFetching && isActiveAllServicesMode) ||
    (pteamServicePackagesSummaryIsFetching &&
      !isActiveAllServicesMode &&
      (serviceId || pteam.services.length > 0))
  )
    return <>{t("loading_packages_summary")}</>;

  const service =
    isActiveAllServicesMode || !serviceId
      ? undefined
      : pteam.services.find((service) => service.service_id === serviceId);

  const handleSBOMUploaded = () => {};

  if (!serviceId) {
    if (pteam.services.length === 0) {
      return (
        <>
          <Box display="flex" flexDirection="row">
            <PTeamLabel pteamId={pteamId} defaultTabIndex={0} />
            <Box flexGrow={1} />
          </Box>
          <SBOMDropArea pteamId={pteamId} onUploaded={handleSBOMUploaded} />
        </>
      );
    }
  }

  let priorityFilters = params.getAll("priorityFilter").filter((filter) =>
    Object.values(getSsvcPriorityProps())
      .map((prop) => prop.displayName)
      .includes(filter),
  );

  const summary = isActiveAllServicesMode
    ? pteamAllServicesPackagesSummary
    : pteamServicePackagesSummary;
  const filteredPackages = summary.packages.filter(
    (packageInfo) =>
      (priorityFilters.length === 0
        ? true // show all if selected none
        : priorityFilters.includes(
            getSsvcPriorityProps()[packageInfo.ssvc_priority || "defer"].displayName,
          )) &&
      (!searchWord?.length > 0 ||
        (packageInfo.package_name + ":" + packageInfo.ecosystem)
          .toLowerCase()
          .includes(searchWord)),
  );

  let tmp;
  const perPage = (tmp = parseInt(params.get("perPage"))) > 0 ? tmp : 10;
  const numPages = Math.ceil(filteredPackages.length / perPage);
  const page = (tmp = parseInt(params.get("page"))) > 0 ? (tmp > numPages ? numPages : tmp) : 1;
  if (tmp !== page) {
    params.set("page", page); // fix for the next
  }
  const targetPackages = filteredPackages.slice(perPage * (page - 1), perPage * page);

  const filterRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
      <Pagination
        shape="rounded"
        page={page}
        count={numPages}
        siblingCount={isSmDown ? 0 : undefined}
        boundaryCount={isSmDown ? 0 : undefined}
        onChange={(event, value) => {
          params.set("page", value);
          navigate(location.pathname + "?" + params.toString());
        }}
      />
      <Select
        size="small"
        variant="standard"
        value={perPage}
        onChange={(event) => {
          if (perPage === event.target.value) return;
          params.set("perPage", event.target.value);
          params.set("page", 1);
          navigate(location.pathname + "?" + params.toString());
        }}
      >
        {[10, 20, 50, 100].map((num) => (
          <MenuItem key={num} value={num} sx={{ justifyContent: "flex-end" }}>
            <Typography variant="body2" sx={{ mt: 0.3 }}>
              {num} {t("rows")}
            </Typography>
          </MenuItem>
        ))}
      </Select>
      <Box flexGrow={1} />
    </Box>
  );

  const handleChangeService = (serviceId) => {
    const newParams = new URLSearchParams();
    newParams.set("pteamId", pteamId);
    newParams.set("serviceId", serviceId);
    if (searchWord) {
      newParams.set("word", searchWord);
    }

    const MytasksParam = preserveMyTasksParam(location.search);
    for (const [key, value] of MytasksParam) {
      newParams.set(key, value);
    }

    navigate(location.pathname + "?" + newParams.toString());
  };

  const handleSearchWord = (word) => {
    params.set("word", word);
    if (word !== searchWord) {
      params.set("page", 1); // reset page
    }
    navigate(location.pathname + "?" + params.toString());
  };

  function navigatePackagePage(targetServiceId, packageId) {
    const preservedParams = preserveParams(location.search);
    preservedParams.set("serviceId", targetServiceId);
    navigate(`/packages/${packageId}?${preservedParams.toString()}`);
  }

  const handleNavigateServiceList = (packageId, packageName, serviceIds) => {
    if (serviceIds.length === 1) {
      navigatePackagePage(serviceIds[0], packageId);
    } else {
      setSelectedPackageInfo({
        packageId: packageId,
        packageName: packageName,
        serviceIds: serviceIds,
      });
      setPTeamServicesListModalOpen(true);
    }
  };

  const handleNavigatePackage = (targetServiceId, packageId) =>
    navigatePackagePage(targetServiceId, packageId);

  const handleAllServices = () => {
    setIsActiveUploadMode(0);
    if (params.get("priorityFilter")) {
      params.delete("priorityFilter");
    }
    if (params.get("page")) {
      params.delete("page");
    }
    if (params.get("perPage")) {
      params.delete("perPage");
    }

    if (isActiveAllServicesMode) {
      params.set("allservices", "off");
      navigate(location.pathname + "?" + params.toString());
    } else {
      params.set("allservices", "on");
      navigate(location.pathname + "?" + params.toString());
    }
  };

  const handleSwitchExpandService = () => setExpandService(!expandService);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const SSVCPriorityMenu = (
    <>
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={searchMenuOpen}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
        sx={{ left: -55 }}
      >
        {sortedSSVCPriorities.map((priorityApiKey) => {
          const priorityProp = getSsvcPriorityProps()[priorityApiKey];
          const priorityDisplayName = priorityProp.displayName;
          const checked = priorityFilters.includes(priorityDisplayName);
          const summary = isActiveAllServicesMode
            ? pteamAllServicesPackagesSummary
            : pteamServicePackagesSummary;
          const ssvcPriorityCount = summary.ssvc_priority_count[priorityApiKey];

          const fixedSx = {
            ...(checked && {
              bgcolor: grey[200],
            }),
          };

          const onClick = () => {
            if (checked) {
              priorityFilters = priorityFilters.filter((filter) => filter !== priorityDisplayName);
            } else {
              priorityFilters.push(priorityDisplayName);
            }
            params.delete("priorityFilter");
            priorityFilters.map((filter) => params.append("priorityFilter", filter));

            params.set("page", 1); // reset page
            navigate(location.pathname + "?" + params.toString());
          };

          return (
            <MenuList dense sx={{ width: 320, ...fixedSx }} key={priorityApiKey}>
              <MenuItem onClick={onClick}>
                {checked ? (
                  <>
                    <ListItemIcon>
                      <CheckIcon />
                    </ListItemIcon>
                    <ListItemText>{priorityDisplayName}</ListItemText>
                  </>
                ) : (
                  <>
                    <ListItemText inset>{priorityDisplayName}</ListItemText>
                  </>
                )}
                {ssvcPriorityCount > ssvcPriorityCountMax ? (
                  <Chip sx={{ ml: -1.5, mr: 2 }} size="small" label={ssvcPriorityCountMax + "+"} />
                ) : (
                  <Chip sx={{ ml: -1.5, mr: 2 }} size="small" label={ssvcPriorityCount} />
                )}
              </MenuItem>
            </MenuList>
          );
        })}
      </Menu>
    </>
  );

  return (
    <>
      <Box display="flex" flexDirection="row">
        <PTeamLabel pteamId={pteamId} defaultTabIndex={0} />
        <Box flexGrow={1} />
      </Box>
      <Box display="flex" flexDirection="row-reverse" sx={{ marginTop: 0 }}>
        <DeleteServiceIcon pteamId={pteamId} onServiceDeleted={handleServiceDeleted} />
        <FormControlLabel
          control={
            <Android12Switch checked={isActiveAllServicesMode} onChange={handleAllServices} />
          }
          label={t("all_services")}
        />
      </Box>
      {!isActiveAllServicesMode &&
        (isMdDown ? (
          <PTeamServiceSelectDialog
            services={pteam.services}
            currentServiceId={serviceId}
            onChangeService={handleChangeService}
            setIsActiveUploadMode={setIsActiveUploadMode}
          />
        ) : (
          <PTeamServiceTabs
            services={pteam.services}
            currentServiceId={serviceId}
            onChangeService={handleChangeService}
            setIsActiveUploadMode={setIsActiveUploadMode}
          />
        ))}
      <CustomTabPanel value={isActiveUploadMode} index={0}>
        {service && (
          <PTeamServiceDetailsResponsive
            pteamId={pteamId}
            service={service}
            expandService={expandService}
            onSwitchExpandService={handleSwitchExpandService}
            highestSsvcPriority={pteamServicePackagesSummary.packages[0]?.ssvc_priority ?? "defer"}
          />
        )}
        <Box
          sx={{
            display: "flex",
            flexDirection: { md: "row", xs: "column" },
            justifyContent: "space-between",
            mt: 2,
          }}
        >
          {filterRow}
          <Box mb={0.5} sx={{ display: "flex", flexDirection: "row", gap: 1 }}>
            <SearchField word={searchWord} onApply={handleSearchWord} />
            <IconButton
              id="basic-button"
              aria-controls={searchMenuOpen ? "basic-menu" : undefined}
              aria-haspopup="true"
              aria-expanded={searchMenuOpen ? "true" : undefined}
              onClick={handleClick}
              size="small"
              sx={{ mt: 1.5 }}
            >
              {searchMenuOpen ? <RemoveCircleOutlineIcon /> : <AddCircleOutlineRoundedIcon />}
            </IconButton>
            {SSVCPriorityMenu}
          </Box>
        </Box>
        <TableContainer component={Paper} sx={{ mt: 0.5 }}>
          <Table sx={{ minWidth: 320 }} aria-label="simple table">
            <TableBody>
              {isActiveAllServicesMode ? (
                <>
                  {targetPackages.map((packageInfo) => (
                    <ErrorBoundary
                      key={packageInfo.package_id}
                      FallbackComponent={PTeamStatusCardFallback}
                    >
                      <PTeamStatusCard
                        key={packageInfo.package_id}
                        onHandleClick={() =>
                          handleNavigateServiceList(
                            packageInfo.package_id,
                            packageInfo.package_name,
                            packageInfo.service_ids,
                          )
                        }
                        pteam={pteam}
                        packageInfo={packageInfo}
                        serviceIds={packageInfo.service_ids}
                      />
                    </ErrorBoundary>
                  ))}
                </>
              ) : (
                <>
                  {targetPackages.map((packageInfo) => (
                    <ErrorBoundary
                      key={packageInfo.package_id}
                      FallbackComponent={PTeamStatusCardFallback}
                    >
                      <PTeamStatusCard
                        key={packageInfo.package_id}
                        onHandleClick={() =>
                          handleNavigatePackage(serviceId, packageInfo.package_id)
                        }
                        pteam={pteam}
                        packageInfo={packageInfo}
                      />
                    </ErrorBoundary>
                  ))}
                </>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {targetPackages.length > 3 && filterRow}
      </CustomTabPanel>
      <CustomTabPanel value={isActiveUploadMode} index={1}>
        <SBOMDropArea pteamId={pteamId} onUploaded={handleSBOMUploaded} />
      </CustomTabPanel>
      <PTeamServicesListModal
        onSetShow={setPTeamServicesListModalOpen}
        show={pTeamServicesListModalOpen}
        packageId={selectedPackageInfo.packageId}
        packageName={selectedPackageInfo.packageName}
        serviceIds={selectedPackageInfo.serviceIds}
      />
    </>
  );
}
