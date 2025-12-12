import { Search as SearchIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  FormControlLabel,
  Select,
  Typography,
  MenuItem,
  Pagination,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Android12Switch } from "../../components/Android12Switch";
import styles from "../../cssModule/button.module.css";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetVulnsQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import { createUpdateParamsFunction } from "../../utils/urlUtils";

import { VulnManagementCardList } from "./VulnManagementCardList";
import { VulnManagementTable } from "./VulnManagementTable";
import { VulnSearchModal } from "./VulnSearchModal";

export function VulnManagement() {
  const perPageItems = [10, 20, 50, 100];

  const [searchMenuOpen, setSearchMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(useLocation().search);
  const pteamId = params.get("pteamId");
  const checkedPteam = params.get("related") !== "off" && pteamId ? true : false;
  const page = parseInt(params.get("page")) || 1;
  const perPage = parseInt(params.get("perPage")) || perPageItems[0];
  const getSearchConditionsFromURL = () => {
    const conditions = {};

    // titleWords
    const titleWords = params.get("titleWords");
    if (titleWords) {
      conditions.title_words = titleWords.split("|");
    }

    // cveIds
    const cveIds = params.get("cveIds");
    if (cveIds) {
      conditions.cve_ids = cveIds.split("|");
    }

    // vulnIds
    const vulnIds = params.get("vulnIds");
    if (vulnIds) {
      conditions.vuln_ids = vulnIds.split("|");
    }

    // creatorIds
    const creatorIds = params.get("creatorIds");
    if (creatorIds) {
      conditions.creator_ids = creatorIds.split("|");
    }

    // updatedAfter
    const updatedAfter = params.get("updatedAfter");
    if (updatedAfter) {
      conditions.updated_after = updatedAfter;
    }

    // updatedBefore
    const updatedBefore = params.get("updatedBefore");
    if (updatedBefore) {
      conditions.updated_before = updatedBefore;
    }

    // minCvssV3Score
    const minCvssV3Score = params.get("minCvssV3Score");
    if (minCvssV3Score !== null && minCvssV3Score !== "") {
      conditions.min_cvss_v3_score = parseFloat(minCvssV3Score);
    }

    // maxCvssV3Score
    const maxCvssV3Score = params.get("maxCvssV3Score");
    if (maxCvssV3Score !== null && maxCvssV3Score !== "") {
      conditions.max_cvss_v3_score = parseFloat(maxCvssV3Score);
    }

    return conditions;
  };

  const searchConditions = getSearchConditionsFromURL();

  const skip = useSkipUntilAuthUserIsReady();

  const getVulnsParams = {
    offset: perPage * (page - 1),
    limit: perPage,
    sort_keys: ["-updated_at", "-cvss_v3_score"],
    pteam_id: checkedPteam === true && pteamId ? pteamId : null,
    ...searchConditions,
  };
  const {
    data: vulnsList,
    error: vulnsError,
    isLoading: vulnsIsLoading,
  } = useGetVulnsQuery({ query: getVulnsParams }, { skip, refetchOnMountOrArgChange: true });

  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

  if (skip) return <>Now loading auth token...</>;
  if (vulnsError)
    throw new APIError(errorToString(vulnsError), {
      api: "getVulns",
    });
  if (vulnsIsLoading) return <>Now loading Vulns...</>;

  const pageMax = Math.ceil((vulnsList?.num_vulns ?? 0) / perPage);

  const handleSearch = (params) => {
    setSearchMenuOpen(false);

    const newParams = {
      page: 1,
      titleWords: params.titleWords || "",
      cveIds: params.cveIds || "",
      vulnIds: params.vulnIds || "",
      creatorIds: params.creatorIds || "",
      updatedAfter: params.updatedAfter || "",
      updatedBefore: params.updatedBefore || "",
      minCvssV3Score: params.minCvssV3Score ?? "",
      maxCvssV3Score: params.maxCvssV3Score ?? "",
    };
    updateParams(newParams);
  };

  const handleCancel = () => {
    setSearchMenuOpen(false);
  };

  const handleChangeSwitch = () => {
    if (pteamId) {
      const currentCheckedPteam = params.get("related") !== "off";
      const newCheckedPteam = !currentCheckedPteam;

      updateParams({
        related: newCheckedPteam ? "on" : "off",
        page: 1, // page reset
      });
    }
  };

  const updateParams = createUpdateParamsFunction(location, navigate);

  const filterRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
      <Pagination
        shape="rounded"
        page={page}
        count={pageMax}
        siblingCount={isMdDown ? 1 : undefined}
        boundaryCount={isMdDown ? 0 : undefined}
        onChange={(event, value) => {
          updateParams({ page: value });
        }}
      />
      <Select
        size="small"
        variant="standard"
        value={perPage}
        onChange={(event) => {
          const newPerPage = event.target.value;
          updateParams({ perPage: newPerPage, page: 1 });
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
      {isMdDown ? (
        <VulnManagementCardList vulns={vulnsList.vulns} />
      ) : (
        <VulnManagementTable vulns={vulnsList.vulns} />
      )}
      {filterRow}
      <VulnSearchModal show={searchMenuOpen} onSearch={handleSearch} onCancel={handleCancel} />
    </>
  );
}
