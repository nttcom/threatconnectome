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
  Tab,
  Table,
  TableBody,
  TableContainer,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import Android12Switch from "../components/Android12Switch";
import { PTeamLabel } from "../components/PTeamLabel";
import { PTeamServiceTabs } from "../components/PTeamServiceTabs";
import { PTeamStatusCard } from "../components/PTeamStatusCard";
import { SBOMDropArea } from "../components/SBOMDropArea";
import { getPTeam, getPTeamServiceTagsSummary, setPTeamId } from "../slices/pteam";
import { noPTeamMessage, threatImpactName, threatImpactProps } from "../utils/const";
const threatImpactCountMax = 99999;

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

export function Status() {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const params = new URLSearchParams(location.search);
  const searchWord = params.get("word")?.trim().toLowerCase() ?? "";

  const pteamId = params.get("pteamId");
  const serviceId = params.get("serviceId");

  const user = useSelector((state) => state.user.user);
  const pteam = useSelector((state) => state.pteam.pteam);
  const summaries = useSelector((state) => state.pteam.serviceTagsSummaries);

  const summary = summaries[serviceId];

  const [anchorEl, setAnchorEl] = React.useState(null);
  const searchMenuOpen = Boolean(anchorEl);

  const [isActiveAllServices, setIsActiveAllServices] = useState(false);

  useEffect(() => {
    if (!user.user_id) return; // wait login completed
    if (!pteamId) return; // wait fixed by App
    if (!pteam) {
      dispatch(getPTeam(pteamId));
      return;
    }
    if (pteam && pteam.pteam_id !== pteamId) {
      // for the case pteam switched. -- looks redundant but necessary, uhmm...
      dispatch(setPTeamId(pteamId));
      return;
    }
    if (summary) return; // Ready!

    if (!serviceId) {
      if (pteam.services.length === 0) return; // nothing to do any more.
      // no service selected. force selecting one of services -- the first one
      const newParams = new URLSearchParams();
      newParams.set("pteamId", pteamId);
      newParams.set("serviceId", pteam.services[0].service_id);
      navigate(location.pathname + "?" + newParams.toString());
      return;
    } else if (!pteam.services.find((service) => service.service_id === serviceId)) {
      alert("Invalid serviceId!");
      const newParams = new URLSearchParams();
      newParams.set("pteamId", pteamId);
      navigate("/?" + newParams.toString());
      return;
    }
    dispatch(getPTeamServiceTagsSummary({ pteamId: pteamId, serviceId: serviceId }));
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [user.user_id, pteamId, pteam, pteamId, serviceId]);

  if (!pteamId) return <>{noPTeamMessage}</>;
  if (!user.user_id || !pteamId || !pteam) {
    return <>Now loading...</>;
  }

  const handleSBOMUploaded = () => {
    dispatch(getPTeam(pteamId));
  };

  if (!serviceId) {
    if (pteam.services.length === 0) {
      return (
        <>
          <Box display="flex" flexDirection="row">
            <PTeamLabel defaultTabIndex={0} />
            <Box flexGrow={1} />
          </Box>
          <SBOMDropArea pteamId={pteamId} onUploaded={handleSBOMUploaded} />
        </>
      );
    }
  }

  if (!summary) return <>Now loading ServiceTagsSummary...</>;

  const iFilter = [0, 1, 2, 3].reduce(
    (ret, idx) => ({
      ...ret,
      [idx]: (params.get("iFilter") ?? "0000")[idx] !== "0",
    }),
    {},
  );

  const filteredTags = summary.tags.filter(
    (tag) =>
      (Object.values(iFilter).every((val) => !val)
        ? true // show all if selected none
        : iFilter[parseInt(tag.threat_impact ?? 4) - 1]) && // show only selected
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

  const handleNavigateTag = (tagId) => {
    for (let key of ["iFilter", "word", "perPage", "page"]) {
      params.delete(key);
    }
    navigate(`/tags/${tagId}?${params.toString()}`);
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const ThreatImpactMenu = (
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
        {[0, 1, 2, 3].map((idx) => {
          const checked = iFilter[idx];
          const threatImpactCount = summary.threat_impact_count[(idx + 1).toString()];

          const fixedSx = {
            ...(checked && {
              bgcolor: grey[200],
            }),
          };

          const impactName = Object.keys(threatImpactProps).includes(idx + 1)
            ? idx + 1
            : threatImpactName[idx + 1];

          const onClick = () => {
            params.set(
              "iFilter",
              [0, 1, 2, 3].reduce(
                (ret, val) =>
                  ret +
                  (val === idx // toggle me only
                    ? checked
                      ? "0"
                      : "1"
                    : iFilter[val] // keep current
                      ? "1"
                      : "0"),
                "",
              ),
            );
            params.set("page", 1); // reset page
            navigate(location.pathname + "?" + params.toString());
          };

          return (
            <MenuList dense sx={{ width: 320, ...fixedSx }} key={idx}>
              <MenuItem onClick={onClick}>
                {checked ? (
                  <>
                    <ListItemIcon>
                      <CheckIcon />
                    </ListItemIcon>
                    <ListItemText>{threatImpactProps[impactName].chipLabel}</ListItemText>
                  </>
                ) : (
                  <>
                    <ListItemText inset>{threatImpactProps[impactName].chipLabel}</ListItemText>
                  </>
                )}
                {threatImpactCount > threatImpactCountMax ? (
                  <Chip sx={{ ml: -1.5, mr: 2 }} size="small" label={threatImpactCountMax + "+"} />
                ) : (
                  <Chip sx={{ ml: -1.5, mr: 2 }} size="small" label={threatImpactCount} />
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
        <PTeamLabel defaultTabIndex={0} />
        <Box flexGrow={1} />
      </Box>
      <Box display="flex" flexDirection="row-reverse" sx={{ marginTop: 0 }}>
        <FormControlLabel
          control={
            <Android12Switch
              checked={isActiveAllServices}
              onChange={() => setIsActiveAllServices(!isActiveAllServices)}
            />
          }
          label="All Services"
        />
      </Box>
      {isActiveAllServices ? (
        <Tabs value={0}>
          <Tab
            label="All"
            sx={{
              textTransform: "none",
              border: `1px solid ${grey[300]}`,
              borderRadius: "0.5rem 0.5rem 0 0",
            }}
          />
        </Tabs>
      ) : (
        <>
          <PTeamServiceTabs
            services={pteam.services}
            currentServiceId={serviceId}
            onChangeService={handleChangeService}
          />
        </>
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
          {ThreatImpactMenu}
        </Box>
      </Box>
      <TableContainer component={Paper} sx={{ mt: 0.5 }}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableBody>
            {targetTags.map((tag) => (
              <PTeamStatusCard
                key={tag.tag_id}
                onHandleClick={() => handleNavigateTag(tag.tag_id)}
                tag={tag}
                isActiveAllServices={isActiveAllServices}
                serviceName={pteam.services[0].service_name}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {targetTags.length > 3 && filterRow}
    </>
  );
}
