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
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router";

import { Android12Switch } from "../components/Android12Switch";
import { DeleteServiceIcon } from "../components/DeleteServiceIcon";
import { PTeamLabel } from "../components/PTeamLabel";
import { PTeamServiceDetails } from "../components/PTeamServiceDetails";
import { PTeamServiceTabs } from "../components/PTeamServiceTabs";
import { PTeamServicesListModal } from "../components/PTeamServicesListModal";
import { PTeamStatusCard } from "../components/PTeamStatusCard";
import { SBOMDropArea } from "../components/SBOMDropArea";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import {
  useGetPTeamQuery,
  useGetPTeamTagsSummaryQuery,
  useGetPTeamServiceTagsSummaryQuery,
} from "../services/tcApi";
import { noPTeamMessage, sortedSSVCPriorities, ssvcPriorityProps } from "../utils/const";
import { errorToString } from "../utils/func";

const ssvcPriorityCountMax = 99999;

function SearchField(props) {
  const { word, onApply } = props;
  const [newWord, setNewWord] = useState(word);

  return (
    <>
      <TextField
        variant="standard"
        label={"Search" + (word === newWord ? "" : " (press ENTER to apply)")}
        size="small"
        value={newWord}
        onChange={(event) => setNewWord(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            onApply(event.target.value);
          }
        }}
        sx={{ textTransform: "none", width: "290px" }}
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
  const [selectedTagInfo, setSelectedTagInfo] = useState({
    tagId: "",
    tagName: "",
    serviceIds: [],
  });

  const skipByAuth = useSkipUntilAuthTokenIsReady();

  const {
    data: pteam,
    error: pteamError,
    isLoading: pteamIsLoading,
  } = useGetPTeamQuery(pteamId, { skip: skipByAuth || !pteamId });

  const {
    currentData: serviceTagsSummary,
    error: serviceTagsSummaryError,
    isFetching: serviceTagsSummaryIsFetching,
  } = useGetPTeamServiceTagsSummaryQuery(
    { pteamId, serviceId },
    { skip: skipByAuth || !pteamId || !serviceId },
  );

  const {
    currentData: pteamTagsSummary,
    error: pteamTagsSummaryError,
    isFetching: pteamTagsSummaryIsFetching,
  } = useGetPTeamTagsSummaryQuery(pteamId, { skip: skipByAuth || !pteamId });

  useEffect(() => {
    if (!pteamId) return; // wait fixed by App
    if (!pteam) return; // wait getQuery

    if (!serviceId) {
      if (pteam.services.length === 0) return; // nothing to do any more.
      // no service selected. force selecting one of services -- the first one
      const newParams = new URLSearchParams();
      newParams.set("pteamId", pteamId);
      newParams.set("serviceId", pteam.services[0].service_id);
      navigate(location.pathname + "?" + newParams.toString());
      return;
    } else if (!pteam.services.find((service) => service.service_id === serviceId)) {
      const newParams = new URLSearchParams();
      newParams.set("pteamId", pteamId);
      navigate("/?" + newParams.toString());
      return;
    }

    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [pteamId, pteam, pteamId, serviceId, isActiveAllServicesMode]);

  if (skipByAuth || !pteamId) return <></>;
  if (!pteamId) return <>{noPTeamMessage}</>;
  if (pteamError) return <>{`Cannot get PTeam: ${errorToString(pteamError)}`}</>;
  if (pteamIsLoading) return <>Now loading PTeam...</>;
  if (serviceTagsSummaryError)
    return <>{`Cannot get serviceTagsSummary: ${errorToString(serviceTagsSummaryError)}`}</>;
  if (serviceId || pteam.services.length > 0) {
    if (!serviceTagsSummary || serviceTagsSummaryIsFetching)
      return <>Now loading serviceTagsSummary...</>;
  }
  if (pteamTagsSummaryError)
    return <>{`Cannot get serviceTagsSummary: ${errorToString(serviceTagsSummaryError)}`}</>;
  if (isActiveAllServicesMode && (!pteamTagsSummary || pteamTagsSummaryIsFetching))
    return <>Now loading pteamTagsSummary...</>;

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

  if (isActiveAllServicesMode) {
    if (!pteamTagsSummary) return <>Now loading PTeamTagsSummary...</>;
  } else {
    if (!serviceTagsSummary) return <>Now loading ServiceTagsSummary...</>;
  }

  let priorityFilters = params.getAll("priorityFilter").filter((filter) =>
    Object.values(ssvcPriorityProps)
      .map((prop) => prop.displayName)
      .includes(filter),
  );

  const summary = isActiveAllServicesMode ? pteamTagsSummary : serviceTagsSummary;
  const filteredTags = summary.tags.filter(
    (tag) =>
      (priorityFilters.length === 0
        ? true // show all if selected none
        : priorityFilters.includes(ssvcPriorityProps[tag.ssvc_priority || "defer"].displayName)) &&
      (!searchWord?.length > 0 || tag.tag_name.toLowerCase().includes(searchWord)),
  );

  let tmp;
  const perPage = (tmp = parseInt(params.get("perPage"))) > 0 ? tmp : 10;
  const numPages = Math.ceil(filteredTags.length / perPage);
  const page = (tmp = parseInt(params.get("page"))) > 0 ? (tmp > numPages ? numPages : tmp) : 1;
  if (tmp !== page) {
    params.set("page", page); // fix for the next
  }
  const targetTags = filteredTags.slice(perPage * (page - 1), perPage * page);

  const filterRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
      <Pagination
        shape="rounded"
        page={page}
        count={numPages}
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
              {num} Rows
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
    navigate(location.pathname + "?" + newParams.toString());
  };

  const handleSearchWord = (word) => {
    params.set("word", word);
    if (word !== searchWord) {
      params.set("page", 1); // reset page
    }
    navigate(location.pathname + "?" + params.toString());
  };

  function navigateArtifactPage(tagId) {
    for (let key of ["priorityFilter", "word", "perPage", "page", "allservices"]) {
      params.delete(key);
    }
    navigate(`/tags/${tagId}?${params.toString()}`);
  }

  const handleNavigateServiceList = (tagId, tagName, serviceIds) => {
    if (serviceIds.length === 1) {
      params.set("serviceId", serviceIds[0]);
      navigateArtifactPage(tagId);
    } else {
      setSelectedTagInfo({ tagId: tagId, tagName: tagName, serviceIds: serviceIds });
      setPTeamServicesListModalOpen(true);
    }
  };

  const handleNavigateTag = (tagId) => navigateArtifactPage(tagId);

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
      params.delete("allservices");
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
          const priorityProp = ssvcPriorityProps[priorityApiKey];
          const priorityDisplayName = priorityProp.displayName;
          const checked = priorityFilters.includes(priorityDisplayName);
          const summary = isActiveAllServicesMode ? pteamTagsSummary : serviceTagsSummary;
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
        <DeleteServiceIcon pteamId={pteamId} />
        <FormControlLabel
          control={
            <Android12Switch checked={isActiveAllServicesMode} onChange={handleAllServices} />
          }
          label="All Services"
        />
      </Box>
      {!isActiveAllServicesMode && (
        <PTeamServiceTabs
          services={pteam.services}
          currentServiceId={serviceId}
          onChangeService={handleChangeService}
          setIsActiveUploadMode={setIsActiveUploadMode}
        />
      )}
      <CustomTabPanel value={isActiveUploadMode} index={0}>
        {service && (
          <PTeamServiceDetails
            pteamId={pteamId}
            service={service}
            expandService={expandService}
            onSwitchExpandService={handleSwitchExpandService}
            highestSsvcPriority={serviceTagsSummary.tags[0]?.ssvc_priority ?? "defer"}
          />
        )}
        <Box display="flex" mt={2}>
          {filterRow}
          <Box flexGrow={1} />
          <Box mb={0.5}>
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
          <Table sx={{ minWidth: 650 }} aria-label="simple table">
            <TableBody>
              {isActiveAllServicesMode ? (
                <>
                  {targetTags.map((tag) => (
                    <PTeamStatusCard
                      key={tag.tag_id}
                      onHandleClick={() =>
                        handleNavigateServiceList(tag.tag_id, tag.tag_name, tag.service_ids)
                      }
                      pteam={pteam}
                      tag={tag}
                      serviceIds={tag.service_ids}
                    />
                  ))}
                </>
              ) : (
                <>
                  {targetTags.map((tag) => (
                    <PTeamStatusCard
                      key={tag.tag_id}
                      onHandleClick={() => handleNavigateTag(tag.tag_id)}
                      pteam={pteam}
                      tag={tag}
                    />
                  ))}
                </>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        {targetTags.length > 3 && filterRow}
      </CustomTabPanel>
      <CustomTabPanel value={isActiveUploadMode} index={1}>
        <SBOMDropArea pteamId={pteamId} onUploaded={handleSBOMUploaded} />
      </CustomTabPanel>
      <PTeamServicesListModal
        onSetShow={setPTeamServicesListModalOpen}
        show={pTeamServicesListModalOpen}
        tagId={selectedTagInfo.tagId}
        tagName={selectedTagInfo.tagName}
        serviceIds={selectedTagInfo.serviceIds}
      />
    </>
  );
}
