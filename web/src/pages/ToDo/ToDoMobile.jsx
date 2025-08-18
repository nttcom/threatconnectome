import ChevronRightIcon from "@mui/icons-material/ChevronRight"; // アイコンを追加
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import SearchIcon from "@mui/icons-material/Search";
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Divider,
  Grid,
  InputAdornment,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

const mockTasks = [
  { cve: "CVE-2025-43859", service: "test2", assignee: "user1@demo.test", ssvc: "SCHEDULED" },
  {
    cve: "CVE-2025-12345",
    service: "auth-service",
    assignee: "user2@demo.test",
    ssvc: "IMMEDIATE",
  },
  {
    cve: "CVE-2024-98765",
    service: "database-api",
    assignee: "user3@demo.test",
    ssvc: "OUT_OF_CYCLE",
  },
];

// --- Helper Function (変更なし) ---
const getSsvcChipColor = (ssvc) => {
  switch (ssvc) {
    case "SCHEDULED":
      return "warning";
    case "IMMEDIATE":
      return "error";
    case "OUT_OF_CYCLE":
      return "info";
    default:
      return "default";
  }
};

export default function VulnerabilityTodoList() {
  return (
    <>
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
              border: "1px solid #e0e0e0",
            },
          }}
        />
      </Box>
      <Stack spacing={3}>
        {mockTasks.map((task) => (
          <Card
            key={task.cve}
            sx={{
              backgroundColor: "#ffffff",
              borderRadius: "16px",
              boxShadow: "none",
              border: "2px solid #e0e0e0",
              transition: "border-color 0.2s ease",
              "&:hover": {
                borderColor: "#c0c0c0",
              },
            }}
          >
            <CardContent sx={{ pt: 3, px: 3 }}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 2,
                }}
              >
                <Typography variant="h6" component="div" fontWeight={600}>
                  {task.cve}
                </Typography>
                <Chip
                  label={task.ssvc}
                  color={getSsvcChipColor(task.ssvc)}
                  size="small"
                  variant="filled"
                  sx={{ fontWeight: 500 }}
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    担当者
                  </Typography>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, mt: 0.5 }}>
                    <PersonOutlineIcon fontSize="small" color="action" />
                    <Typography variant="body2" noWrap>
                      {task.assignee}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">
                    サービス
                  </Typography>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, mt: 0.5 }}>
                    <DnsOutlinedIcon fontSize="small" color="action" />
                    <Typography variant="body2" noWrap>
                      {task.service}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>

            <CardActions sx={{ p: 2 }}>
              <Button
                size="medium"
                variant="contained"
                color="primary"
                fullWidth
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
        ))}
      </Stack>
    </>
  );
}
