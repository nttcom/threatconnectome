import {
  CheckCircleOutline as CheckCircleOutlineIcon,
  HorizontalRule as HorizontalRuleIcon,
  Info as InfoIcon,
  Search as SearchIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  FormControlLabel,
  Select,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
  MenuItem,
  Pagination,
  Paper,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router";
import { useLocation } from "react-router-dom";

import { FormattedDateTimeWithTooltip } from "../components/FormattedDateTimeWithTooltip";
import { TopicSearchModal } from "../components/TopicSearchModal";
import styles from "../cssModule/button.module.css";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useSearchTopicsQuery } from "../services/tcApi";
import { getActions, getTopic } from "../slices/topics";
import { difficulty, difficultyColors } from "../utils/const";
import { errorToString } from "../utils/func";

function TopicManagementTableRow(props) {
  const { topicId } = props;

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const topics = useSelector((state) => state.topics.topics);
  const actions = useSelector((state) => state.topics.actions);
  const params = new URLSearchParams(location.search);

  useEffect(() => {
    if (topics?.[topicId] === undefined) dispatch(getTopic(topicId));
    if (actions?.[topicId] === undefined) dispatch(getActions(topicId));
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, []);

  const topic = topics?.[topicId];
  const actionList = actions?.[topicId];

  if (!topic) {
    return (
      <TableRow>
        <TableCell>Loading...</TableCell>
      </TableRow>
    );
  }

  return (
    <TableRow
      key={topic.topic_id}
      sx={{
        height: 80,
        cursor: "pointer",
        "&:last-child td, &:last-child th": { border: 0 },
        "&:hover": { bgcolor: grey[100] },
        borderLeft: `solid 5px ${difficultyColors[difficulty[topic.threat_impact - 1]]}`,
      }}
      onClick={() => navigate(`/topics/${topic.topic_id}?${params.toString()}`)}
    >
      <TableCell>
        <FormattedDateTimeWithTooltip utcString={topic.updated_at} />
      </TableCell>
      <TableCell align="center">
        {actionList?.length > 0 ? (
          <CheckCircleOutlineIcon color="success" />
        ) : (
          <HorizontalRuleIcon sx={{ color: grey[500] }} />
        )}
      </TableCell>
      <TableCell>
        <Typography variant="subtitle1" sx={{ overflowWrap: "anywhere" }}>
          {topic.title}
        </Typography>
      </TableCell>
      <TableCell>
        {topic.misp_tags.map((misp_tag) => (
          <Chip
            key={misp_tag.tag_id}
            label={misp_tag.tag_name}
            size="small"
            sx={{ m: 0.5, borderRadius: 0.5 }}
          />
        ))}
      </TableCell>
    </TableRow>
  );
}
TopicManagementTableRow.propTypes = {
  topicId: PropTypes.string.isRequired,
};

export function TopicManagement() {
  const perPageItems = [10, 20, 50, 100];

  const [searchMenuOpen, setSearchMenuOpen] = useState(false);
  const [checkedPteam, setCheckedPteam] = useState(true);
  const [checkedAteam, setCheckedAteam] = useState(false);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(perPageItems[0]);
  const [searchConditions, setSearchConditions] = useState({});

  const skip = useSkipUntilAuthTokenIsReady();

  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");
  const ateamId = params.get("ateamId");

  const searchParams = {
    offset: perPage * (page - 1),
    limit: perPage,
    sort_key: "updated_at_desc",
    pteam_id: checkedPteam === true && pteamId ? pteamId : null,
    ateam_id: checkedAteam === true && ateamId ? ateamId : null,
    ...searchConditions,
  };
  const {
    data: searchResult,
    error: searchResultError,
    isLoading: searchResultIsLoading,
  } = useSearchTopicsQuery(searchParams, { skip, refetchOnMountOrArgChange: true });

  if (searchResultError) return <>{`Search topics failed: ${errorToString(searchResultError)}`}</>;
  if (searchResultIsLoading || !searchResult) return <>Now searching topics...</>;

  const topics = searchResult.topics;
  const pageMax = Math.ceil((searchResult?.num_topics ?? 0) / perPage);

  const paramsToSearchQuery = (params) => {
    const delimiter = "|";
    let query = {};
    if (params?.titleWords?.length > 0) query.title_words = params.titleWords.split(delimiter);
    if (params?.mispTags?.length > 0) query.misp_tag_names = params.mispTags.split(delimiter);
    if (params?.topicIds?.length > 0) query.topic_ids = params.topicIds.split(delimiter);
    if (params?.creatorIds?.length > 0) query.creator_ids = params.creatorIds.split(delimiter);
    if (params?.updatedAfter) query.updated_after = params.updatedAfter;
    if (params?.updatedBefore) query.updated_before = params.updatedBefore;
    return query;
  };

  const handleSearch = (params) => {
    setSearchMenuOpen(false);
    setPage(1); // reset page for new search result
    setSearchConditions(paramsToSearchQuery(params));
  };

  const handleCancel = () => {
    setSearchMenuOpen(false);
  };

  const handleChangeSwitch = () => {
    if (pteamId) {
      setCheckedPteam(!checkedPteam);
    } else if (ateamId) {
      setCheckedAteam(!checkedAteam);
    }
  };

  const filterRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
      <Pagination
        shape="rounded"
        page={page}
        count={pageMax}
        onChange={(event, value) => setPage(value)}
      />
      <Select
        size="small"
        variant="standard"
        value={perPage}
        onChange={(event) => {
          setPage(1); // reset page for new perPage
          setPerPage(event.target.value);
        }}
      >
        {perPageItems.map((num) => (
          <MenuItem key={num} value={num} sx={{ justifyContent: "space-between" }}>
            <Typography variant="body2" sx={{ mt: 0.3 }}>
              {num} Rows
            </Typography>
          </MenuItem>
        ))}
      </Select>
      <Box flexGrow={1} />
    </Box>
  );

  const Android12Switch = styled(Switch)(({ theme }) => ({
    padding: 8,
    "& .MuiSwitch-track": {
      borderRadius: 22 / 2,
      "&:before, &:after": {
        content: "''",
        position: "absolute",
        top: "50%",
        transform: "translateY(-50%)",
        width: 16,
        height: 16,
      },
      "&:before": {
        backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
          theme.palette.getContrastText(theme.palette.primary.main),
        )}" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>")`,
        left: 12,
      },
      "&:after": {
        backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 24 24"><path fill="${encodeURIComponent(
          theme.palette.getContrastText(theme.palette.primary.main),
        )}" d="M19,13H5V11H19V13Z" /></svg>")`,
        right: 12,
      },
    },
    "& .MuiSwitch-thumb": {
      boxShadow: "none",
      width: 16,
      height: 16,
      margin: 2,
    },
  }));

  return (
    <>
      <Box display="flex" mt={2}>
        {pteamId ? (
          <FormControlLabel
            sx={{ ml: -1 }}
            control={<Android12Switch checked={checkedPteam} onChange={handleChangeSwitch} />}
            label="Related topics"
          />
        ) : (
          <FormControlLabel
            sx={{ ml: -1 }}
            control={<Android12Switch checked={checkedAteam} onChange={handleChangeSwitch} />}
            label="Related topics"
          />
        )}

        <Box flexGrow={1} />
        <Box mb={0.5}>
          <Button
            className={styles.prominent_btn}
            onClick={() => {
              setSearchMenuOpen(true);
            }}
          >
            <SearchIcon />
          </Button>
        </Box>
      </Box>
      <TableContainer
        component={Paper}
        sx={{
          mt: 1,
          border: `1px solid ${grey[300]}`,
          "&:before": { display: "none" },
        }}
      >
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              <TableCell style={{ width: "20%" }} display="flex">
                <Box display="flex" flexDirection="row">
                  <Typography variant="body2" sx={{ fontWeight: 900 }}>
                    Last Update
                  </Typography>
                  <Tooltip title="Timezone is local time">
                    <InfoIcon sx={{ color: grey[600], ml: 1 }} />
                  </Tooltip>
                </Box>
              </TableCell>
              <TableCell style={{ width: "3%", fontWeight: 900 }}>Action</TableCell>
              <TableCell style={{ width: "25%", fontWeight: 900 }}>Title</TableCell>
              <TableCell style={{ width: "35%", fontWeight: 900 }}>MISP Tag</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {topics?.length > 0 ? (
              topics.map((topic) => (
                <TopicManagementTableRow key={topic.topic_id} topicId={topic.topic_id} />
              ))
            ) : (
              <TableRow>
                <TableCell>No topics</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      {filterRow}
      <TopicSearchModal show={searchMenuOpen} onSearch={handleSearch} onCancel={handleCancel} />
    </>
  );
}
