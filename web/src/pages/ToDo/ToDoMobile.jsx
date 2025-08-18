import SearchIcon from "@mui/icons-material/Search";
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Container,
  CssBaseline,
  InputAdornment,
  TextField,
  Toolbar,
  Typography,
  Chip,
  Stack,
} from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";

import { Android12Switch } from "../../components/Android12Switch";

// サンプルデータ
const mockTasks = [
  {
    cve: "CVE-2025-43859",
    team: "Metemcyber開発チーム 東京",
    service: "test2",
    package: "h11",
    assignee: "user1@demo.test",
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

// SSVCステータスに応じてChipの色を決定する関数
const getSsvcChipColor = (ssvc) => {
  switch (ssvc) {
    case "SCHEDULED":
      return "warning"; // 黄色
    case "IMMEDIATE":
      return "error"; // 赤色
    case "OUT_OF_CYCLE":
      return "info"; // 青色
    default:
      return "default"; // デフォルト
  }
};

export default function VulnerabilityTodoList() {
  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <Android12Switch />
        <Typography>My tasks</Typography>
      </Box>
      {/* Search Bar */}
      <Box mb={1}>
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
          }}
        />
      </Box>

      {/* Task Cards */}
      <Stack spacing={2}>
        {mockTasks.map((task) => (
          <Card key={task.cve} variant="outlined">
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                }}
              >
                <Typography variant="h6" component="div" gutterBottom>
                  {task.cve}
                </Typography>
                <Chip label={task.ssvc} color={getSsvcChipColor(task.ssvc)} size="small" />
              </Box>

              <Typography color="text.secondary" sx={{ mb: 1.5 }}>
                担当者: {task.assignee}
              </Typography>
              <Typography variant="body2">サービス: {task.service}</Typography>
            </CardContent>
            <CardActions>
              <Button size="small">詳細を見る</Button>
            </CardActions>
          </Card>
        ))}
      </Stack>
    </>
  );
}
