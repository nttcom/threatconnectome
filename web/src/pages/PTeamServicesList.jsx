import { KeyboardDoubleArrowRight as KeyboardDoubleArrowRightIcon } from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  Typography,
  CardHeader,
  CardActions,
  Link,
  MenuItem,
  Pagination,
  Select,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useState } from "react";

// sample data
const sampleServiceList = [
  {
    sampleId: 1,
    sampleService: "webapp-frontend",
    sampleExe:
      "A front-end framework is a JavaScript framework responsible for developing the user interface of an application, often a web application, which usually involves structuring the file system, binding data to DOM¹ elements, styling components, configuring routing, and performing AJAX² requests. A front-end framework is a JavaScript framework responsible for developing the user interface of an application, often a web application, which usually involves structuring the file system, binding data to DOM¹ elements, styling components, configuring routing, and performing AJAX² requests.A front-end framework is a JavaScript framework responsible for developing the user interface of an application, often a web application, which usually involves structuring the file system, binding data to DOM¹ elements, styling components, configuring routing, and performing AJAX² requests.",
    sampleUrl: "https://github.com/wedapp-frontend",
  },
  {
    sampleId: 2,
    sampleService: "webapp-backend",
    sampleExe: "A back-end framework is a JavaScript framework responsible.",
    sampleUrl: "https://github.com/wedapp-backend",
  },
];

const sampleChoiceArtifact = "asynckit:npm:npm";

function textTrim(selector) {
  const maxWordCount = 800;
  const clamp = "…";
  if (selector.length > maxWordCount) {
    selector = selector.substr(0, maxWordCount - 1) + clamp; // remove 1 character
  }
  return selector;
}

export function PTeamServicesList() {
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const paginationRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 2 }}>
      <Pagination
        shape="rounded"
        page={page}
        count={10}
        onChange={(event, value) => setPage(value)}
      />
      <Select
        size="small"
        variant="standard"
        value={perPage}
        onChange={(event) => {
          setPerPage(event.target.value);
          setPage(1);
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

  return (
    <>
      <Box display="flex" flexDirection="row" alignItems="center" sx={{ margin: 1 }}>
        <Typography variant="h6">Selected Artifact</Typography>
        <KeyboardDoubleArrowRightIcon sx={{ ml: 0.5, mr: 0.5 }} />
        <Typography variant="h5" fontWeight={900}>
          {sampleChoiceArtifact}
        </Typography>
      </Box>
      <Box alignItems="center" display="flex" flexWrap="wrap" flexDirection="row" flexGrow={1}>
        {paginationRow}
        {sampleServiceList.map((sampleService) => (
          <Card
            key={sampleService.sampleId}
            variant="outlined"
            alignContent="space-between"
            sx={{ margin: 1, width: "100%", "&:hover": { bgcolor: grey[100] } }}
          >
            <CardHeader
              title={sampleService.sampleService}
              sx={{ backgroundColor: grey[200] }}
            ></CardHeader>
            <CardContent>
              <Typography variant="body2">
                {sampleService.sampleExe === ""
                  ? "No Explanation"
                  : textTrim(sampleService.sampleExe)}
              </Typography>
            </CardContent>
            <CardActions sx={{ ml: 1 }}>
              {sampleService.sampleUrl === "" ? (
                <Typography variant="body2" color="text.secondary">
                  No URL
                </Typography>
              ) : (
                <Link variant="body2" href={sampleService.sampleUrl} color="text.secondary">
                  {sampleService.sampleUrl}
                </Link>
              )}
            </CardActions>
          </Card>
        ))}
      </Box>
    </>
  );
}
