import {
  AddCircleOutlineRounded as AddCircleOutlineRoundedIcon,
  Check as CheckIcon,
  Clear as ClearIcon,
  RemoveCircleOutline as RemoveCircleOutlineIcon,
} from "@mui/icons-material";
import {
  Box,
  Chip,
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
import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router";

import { PTeamGroupChip } from "../components/PTeamGroupChip";
import { PTeamLabel } from "../components/PTeamLabel";
import { PTeamStatusCard } from "../components/PTeamStatusCard";
import { SBOMDropArea } from "../components/SBOMDropArea";
import { getPTeamGroups, getPTeamTagsSummary } from "../slices/pteam";
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
  const selectedGroup = params.get("group") ?? "";

  const [anchorEl, setAnchorEl] = React.useState(null);
  const searchMenuOpen = Boolean(anchorEl);

  const user = useSelector((state) => state.user.user);
  const pteamId = useSelector((state) => state.pteam.pteamId); // dispatched by App or PTeamSelector
  const summary = useSelector((state) => state.pteam.tagsSummary); // dispatched by App

  if (!pteamId) return <>{noPTeamMessage}</>;
  else if (!user || !summary) return <>Now loading...</>;

  const handleSBOMUploaded = () => {
    dispatch(getPTeamTagsSummary(pteamId));
    dispatch(getPTeamGroups(pteamId));
  };

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
      (!searchWord?.length > 0 || tag.tag_name.toLowerCase().includes(searchWord)) &&
      (selectedGroup === "" || tag.references.some((ref) => ref.group === selectedGroup)),
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
        <PTeamLabel defaultTabIndex={1} />
        <Box flexGrow={1} />
      </Box>
      <PTeamGroupChip />
      {summary.tags.length === 0 ? (
        <SBOMDropArea pteamId={pteamId} onUploaded={handleSBOMUploaded} />
      ) : (
        <>
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
                    handleClick={() => handleNavigateTag(tag.tag_id)}
                    tag={tag}
                  />
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {targetTags.length > 3 && filterRow}
        </>
      )}
    </>
  );
}
