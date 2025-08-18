import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import GroupOutlinedIcon from "@mui/icons-material/GroupOutlined";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
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
  const lineClampStyle = {
    overflow: "hidden",
    textOverflow: "ellipsis",
    display: "-webkit-box",
    WebkitLineClamp: "2",
    WebkitBoxOrient: "vertical",
    overflowWrap: "break-word",
  };

  return (
    <Box sx={{ p: 2 }}>
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
      <Stack spacing={2}>
        {mockTasks.map((task) => {
          const detailItems = [
            {
              label: "Team",
              value: task.team,
              icon: <GroupOutlinedIcon fontSize="small" color="action" />,
            },
            {
              label: "Package",
              value: task.package,
              icon: <Inventory2OutlinedIcon fontSize="small" color="action" />,
            },
            {
              label: "Assignee",
              value: task.assignee,
              icon: <PersonOutlineIcon fontSize="small" color="action" />,
            },
            {
              label: "Service",
              value: task.service,
              icon: <DnsOutlinedIcon fontSize="small" color="action" />,
            },
          ];

          return (
            <Card
              key={task.cve}
              sx={{
                backgroundColor: "#ffffff",
                borderRadius: "16px",
                boxShadow: "none",
                border: "2px solid #e0e0e0",
                transition: "border-color 0.2s ease",
                "&:hover": { borderColor: "#c0c0c0" },
              }}
            >
              <CardContent sx={{ pt: 2, px: 2 }}>
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
                  <Typography variant="h6" component="div" fontWeight={600}>
                    {task.cve}
                  </Typography>
                  <Chip
                    label={task.ssvc}
                    color={getSsvcChipColor(task.ssvc)}
                    size="small"
                    variant="filled"
                    sx={{ fontWeight: 500, flexShrink: 0 }}
                  />
                </Box>
                <Divider sx={{ my: 2 }} />
                <Grid container rowSpacing={2} columnSpacing={2}>
                  {detailItems.map((item) => (
                    <Grid item xs={12} sm={6} key={item.label}>
                      <Typography variant="caption" color="text.secondary">
                        {item.label}
                      </Typography>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, mt: 0.5 }}>
                        {item.icon}
                        <Typography variant="body2" sx={lineClampStyle}>
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
                  color="primary"
                  endIcon={<ChevronRightIcon />}
                  sx={{ borderRadius: "12px", textTransform: "none", fontWeight: 600, py: 1 }}
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
