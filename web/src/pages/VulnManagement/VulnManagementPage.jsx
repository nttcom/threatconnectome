import { Search as SearchIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  FormControlLabel,
  Select,
  TableContainer,
  Typography,
  MenuItem,
  Pagination,
  Paper,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useState } from "react";
import { useLocation } from "react-router-dom";

import { Android12Switch } from "../../components/Android12Switch";
import styles from "../../cssModule/button.module.css";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetVulnsQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

import { VulnManagementTable } from "./VulnManagementTable";
import { VulnSearchModal } from "./VulnSearchModal";

export function VulnManagement() {
  const perPageItems = [10, 20, 50, 100];

  const [searchMenuOpen, setSearchMenuOpen] = useState(false);
  const [checkedPteam, setCheckedPteam] = useState(true);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(perPageItems[0]);
  const [searchConditions, setSearchConditions] = useState({});

  const skip = useSkipUntilAuthUserIsReady();

  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");

  const getVulnsParams = {
    offset: perPage * (page - 1),
    limit: perPage,
    sort_key: "updated_at_desc",
    pteam_id: checkedPteam === true && pteamId ? pteamId : null,
    ...searchConditions,
  };
  const {
    data: vulns,
    error: vulnsError,
    isLoading: vulnsIsLoading,
  } = useGetVulnsQuery(getVulnsParams, { skip, refetchOnMountOrArgChange: true });

  if (skip) return <>Now loading auth token...</>;
  if (vulnsError)
    throw new APIError(errorToString(vulnsError), {
      api: "getVulns",
    });
  if (vulnsIsLoading) return <>Now loading Vulns...</>;

  const pageMax = Math.ceil((vulns?.length ?? 0) / perPage);

  const paramsToSearchQuery = (params) => {
    const delimiter = "|";
    let query = {};
    if (params?.titleWords?.length > 0) query.title_words = params.titleWords.split(delimiter);
    if (params?.cveIds?.length > 0) query.cve_ids = params.cveIds.split(delimiter);
    if (params?.vulnIds?.length > 0) query.vuln_ids = params.vulnIds.split(delimiter);
    if (params?.creatorIds?.length > 0) query.creator_ids = params.creatorIds.split(delimiter);
    if (params?.updatedAfter) query.updated_after = params.updatedAfter;
    if (params?.updatedBefore) query.updated_before = params.updatedBefore;
    if (params?.minCvssV3Score || params?.minCvssV3Score === 0)
      query.min_cvss_v3_score = params.minCvssV3Score;
    if (params?.maxCvssV3Score || params?.maxCvssV3Score === 0)
      query.max_cvss_v3_score = params.maxCvssV3Score;

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

  return (
    <>
      <Box display="flex" mt={2}>
        {pteamId && (
          <FormControlLabel
            sx={{ ml: -1 }}
            control={<Android12Switch checked={checkedPteam} onChange={handleChangeSwitch} />}
            label="Related vulns"
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
        <VulnManagementTable vulns={vulns} />
      </TableContainer>
      {filterRow}
      <VulnSearchModal show={searchMenuOpen} onSearch={handleSearch} onCancel={handleCancel} />
    </>
  );
}
