import {
  CheckCircleOutline as CheckCircleOutlineIcon,
  Info as InfoIcon,
  Search as SearchIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  Select,
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
import React from "react";

import TopicSearchModal from "../components/TopicSearchModal";
import { difficulty, difficultyColors } from "../utils/const";

const testTopics = [
  {
    lastUpdate: "2023/9/15 14:35:10",
    action: true,
    title: "An issue was discovered in the Linux kernel before 6.3.4",
    threatImpact: 1,
    mispTag: [
      "CVE-2023-38429",
      "CVE-2020-7788",
      "reportlab:pypi:",
      "python-reportlab:debian-10",
      "CVE-2020-7788-CVE-2020-7788",
    ],
  },
  {
    lastUpdate: "2023/9/15 14:35:10",
    action: false,
    title: "invalid kfree in fs/ntfs3/inode.c",
    threatImpact: 2,
    mispTag: ["CVE-2023-0810", "CVE-2020-8870", "python-reportlab:debian-11", "reportlab:pypi:"],
  },
  {
    lastUpdate: "2023/9/16 14:40:10",
    action: true,
    title: "In multiple functions of binder.c, there is a possible memory",
    threatImpact: 3,
    mispTag: ["CVE-2023-0227", "CVE-2020-7788", "python-reportlab:debian-10", "reportlab:pypi:"],
  },
];

export default function TopicManagement() {
  const [searchMenuOpen, setSearchMenuOpen] = React.useState(false);

  const filterRow = (
    <Box display="flex" alignItems="center" sx={{ mt: 1 }}>
      <Pagination shape="rounded" />
      <Select size="small" variant="standard">
        {[10, 20, 50, 100].map((num) => (
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
        {filterRow}
        <Box flexGrow={1} />
        <Box mb={0.5}>
          <Button
            variant="contained"
            color="success"
            sx={{ textTransform: "none" }}
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
              <TableCell style={{ width: "10%" }} display="flex">
                <Box display="flex" flexDirection="row">
                  <Typography variant="body2">Last Update</Typography>
                  <Tooltip title="Timezone is local time">
                    <InfoIcon sx={{ color: grey[600], ml: 1 }} />
                  </Tooltip>
                </Box>
              </TableCell>
              <TableCell style={{ width: "3%" }}>Action</TableCell>
              <TableCell style={{ width: "25%" }}>Title</TableCell>
              <TableCell style={{ width: "35%" }}>MISP Tag</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {testTopics.map((testTopic) => (
              <TableRow
                key={testTopic.name}
                sx={{
                  height: 80,
                  cursor: "pointer",
                  "&:last-child td, &:last-child th": { border: 0 },
                  "&:hover": { bgcolor: grey[100] },
                  borderLeft: `solid 5px ${
                    difficultyColors[difficulty[testTopic.threatImpact - 1]]
                  }`,
                }}
              >
                <TableCell>
                  <Typography sx={{ overflowWrap: "anywhere" }}>{testTopic.lastUpdate}</Typography>
                </TableCell>
                <TableCell>
                  {testTopic.action ? (
                    <CheckCircleOutlineIcon color="success" />
                  ) : (
                    <CheckCircleOutlineIcon sx={{ color: grey[500] }} />
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="subtitle1" sx={{ overflowWrap: "anywhere" }}>
                    {testTopic.title}
                  </Typography>
                </TableCell>
                <TableCell>
                  {testTopic.mispTag.map((misp) => (
                    <Chip label={misp} key={misp} size="small" sx={{ m: 0.5, borderRadius: 0.5 }} />
                  ))}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {filterRow}
      <TopicSearchModal setShow={setSearchMenuOpen} show={searchMenuOpen} />
    </>
  );
}
