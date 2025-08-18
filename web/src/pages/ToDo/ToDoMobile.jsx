import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import FingerprintIcon from "@mui/icons-material/Fingerprint";
import FlagOutlinedIcon from "@mui/icons-material/FlagOutlined";
import GroupOutlinedIcon from "@mui/icons-material/GroupOutlined";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import SearchIcon from "@mui/icons-material/Search";
import SortIcon from "@mui/icons-material/Sort";
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Divider,
  Drawer,
  Grid,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

const mockTasks = [
  {
    cve: "CVE-2025-43859",
    team: "Metemcyber開発チーム 東京 (レガシーシステム担当)",
    service: "test2-main-application-server-instance",
    package: "h11-a-very-long-package-name-for-demonstration",
    assignee: "user1.with.a.very.long.email.address@demo.test",
    ssvc: "SCHEDULED",
  },
  {
    cve: "CVE-2025-12345",
    team: "Frontendチーム",
    service: "auth-service",
    package: "react-v18",
    assignee: "user2@demo.test",
    ssvc: "IMMEDIATE",
  },
  {
    cve: "CVE-2024-98765",
    team: "Backendチーム",
    service: "database-api",
    package: "django-v4",
    assignee: "user3@demo.test",
    ssvc: "OUT_OF_CYCLE",
  },
];

const getSsvcColorInfo = (ssvc) => {
  switch (ssvc) {
    case "SCHEDULED":
      return { main: "#f57c00", glow: "#ffa726" };
    case "IMMEDIATE":
      return { main: "#d32f2f", glow: "#ef5350" };
    case "OUT_OF_CYCLE":
      return { main: "#0288d1", glow: "#29b6f6" };
    default:
      return { main: "#616161", glow: "#9e9e9e" };
  }
};

const sortableKeys = [
  { key: "cve", label: "CVE", icon: <FingerprintIcon /> },
  { key: "team", label: "Team", icon: <GroupOutlinedIcon /> },
  { key: "ssvc", label: "SSVC", icon: <FlagOutlinedIcon /> },
];

export default function VulnerabilityTodoList() {
  const [tasks] = useState(mockTasks);
  const [sortConfig, setSortConfig] = useState({ key: "cve", direction: "ascending" });
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleSortKeyChange = (key) => {
    setSortConfig({ ...sortConfig, key });
  };

  const handleSortDirectionChange = (event, newDirection) => {
    if (newDirection !== null) {
      setSortConfig({ ...sortConfig, direction: newDirection });
    }
  };

  const sortedTasks = useMemo(() => {
    const sortableItems = [...tasks];
    sortableItems.sort((a, b) => {
      const comparison = String(a[sortConfig.key]).localeCompare(String(b[sortConfig.key]));
      return sortConfig.direction === "ascending" ? comparison : -comparison;
    });
    return sortableItems;
  }, [tasks, sortConfig]);

  const currentSortLabel =
    sortableKeys.find((k) => k.key === sortConfig.key)?.label || sortConfig.key;

  return (
    <Box sx={{ p: { xs: 2, sm: 3 } }}>
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search CVE ID"
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            sx: {
              borderRadius: "12px",
              backgroundColor: "background.paper",
              "& fieldset": {
                borderColor: "rgba(0, 0, 0, 0.2)",
              },
            },
          }}
        />
      </Box>

      <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 2 }}>
        <Chip
          icon={<SortIcon />}
          label={`${currentSortLabel} (${sortConfig.direction === "ascending" ? "昇順" : "降順"})`}
          onClick={() => setIsDrawerOpen(true)}
          clickable
        />
      </Box>

      <Drawer
        anchor="bottom"
        open={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        PaperProps={{ sx: { borderTopLeftRadius: 16, borderTopRightRadius: 16 } }}
      >
        <Box sx={{ p: 2, pb: 3 }}>
          <Box
            sx={{
              width: 40,
              height: 5,
              backgroundColor: "grey.300",
              borderRadius: 3,
              mx: "auto",
              mb: 2,
            }}
          />
          <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
            並び替え
          </Typography>
          <ToggleButtonGroup
            value={sortConfig.direction}
            exclusive
            fullWidth
            onChange={handleSortDirectionChange}
            sx={{ mb: 2 }}
          >
            <ToggleButton value="ascending">
              <ArrowUpwardIcon sx={{ mr: 1 }} />
              昇順
            </ToggleButton>
            <ToggleButton value="descending">
              <ArrowDownwardIcon sx={{ mr: 1 }} />
              降順
            </ToggleButton>
          </ToggleButtonGroup>
          <List>
            {sortableKeys.map((item) => (
              <ListItem key={item.key} disablePadding>
                <ListItemButton
                  selected={sortConfig.key === item.key}
                  onClick={() => handleSortKeyChange(item.key)}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Box sx={{ textAlign: "center" }}>
            <Button onClick={() => setIsDrawerOpen(false)} sx={{ mt: 2 }}>
              Close
            </Button>
          </Box>
        </Box>
      </Drawer>

      <Stack spacing={3}>
        {sortedTasks.map((task) => {
          const detailItems = [
            { label: "Team", value: task.team, icon: <GroupOutlinedIcon fontSize="small" /> },
            {
              label: "Package",
              value: task.package,
              icon: <Inventory2OutlinedIcon fontSize="small" />,
            },
            {
              label: "Assignee",
              value: task.assignee,
              icon: <PersonOutlineIcon fontSize="small" />,
            },
            { label: "Service", value: task.service, icon: <DnsOutlinedIcon fontSize="small" /> },
          ];
          const colorInfo = getSsvcColorInfo(task.ssvc);

          return (
            <Card
              key={task.cve}
              sx={{
                borderRadius: 5,
                border: "2px solid rgba(0, 0, 0, 0.15)",
                boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
                cursor: "pointer",
                transition: "transform 0.1s ease-in-out, box-shadow 0.1s ease-in-out",
                "&:active:not(:has(button:active))": {
                  transform: "scale(0.98) translateY(2px)",
                  boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
                },
              }}
            >
              <CardContent sx={{ pt: 3, px: 3 }}>
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: { xs: "column", sm: "row" },
                    alignItems: { xs: "flex-start", sm: "center" },
                    justifyContent: "space-between",
                    gap: { xs: 1, sm: 2 },
                    mb: 2,
                  }}
                >
                  <Typography variant="h6" component="div" fontWeight={600} color="text.primary">
                    {task.cve}
                  </Typography>
                  <Chip
                    label={task.ssvc}
                    size="small"
                    sx={{
                      fontWeight: 600,
                      color: "#fff",
                      backgroundColor: colorInfo.main,
                    }}
                  />
                </Box>
                <Divider sx={{ my: 2, borderColor: "rgba(0, 0, 0, 0.1)" }} />
                <Grid container rowSpacing={2.5} columnSpacing={2}>
                  {detailItems.map((item) => (
                    <Grid item xs={12} sm={6} key={item.label}>
                      <Typography variant="caption" color="text.secondary">
                        {item.label}
                      </Typography>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          mt: 0.5,
                          color: "text.secondary",
                        }}
                      >
                        {item.icon}
                        <Typography
                          variant="body2"
                          color="text.primary"
                          sx={{
                            overflowWrap: "break-word",
                            minWidth: 0,
                          }}
                        >
                          {item.value}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
              <CardActions sx={{ p: 2, justifyContent: "flex-end" }}>
                <Button
                  size="medium"
                  variant="contained"
                  endIcon={<ChevronRightIcon />}
                  sx={{
                    borderRadius: "12px",
                    textTransform: "none",
                    fontWeight: 600,
                    py: 1,
                  }}
                >
                  詳細を見る
                </Button>
              </CardActions>
            </Card>
          );
        })}
      </Stack>
    </Box>
  );
}
