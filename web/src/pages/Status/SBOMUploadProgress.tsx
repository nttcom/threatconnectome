import {
  AccessTime as AccessTimeIcon,
  Close as CloseIcon,
  InsertDriveFile as InsertDriveFileIcon,
  PendingActions as PendingActionsIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";
import {
  Badge,
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  LinearProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from "@mui/material";
import { useState } from "react";

export type UploadProgress = {
  serviceName: string;
  progressPercent: number;
  estimatedCompletionTime: string;
};

type Props = {
  progresses: UploadProgress[];
};

export function SBOMUploadProgress({ progresses }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Tooltip title="アップロード進捗">
        <IconButton onClick={() => setOpen(true)}>
          <Badge variant="dot" color="primary" invisible={progresses.length === 0}>
            <PendingActionsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="md"
        fullWidth
        slotProps={{ paper: { sx: { borderRadius: 3 } } }}
      >
        <DialogTitle
          sx={{
            alignItems: "center",
            bgcolor: "background.soft",
            display: "flex",
            justifyContent: "space-between",
            py: 2,
          }}
        >
          <Box sx={{ alignItems: "center", display: "flex", gap: 2 }}>
            <Box
              sx={{
                bgcolor: "primary.light",
                borderRadius: 2,
                color: "primary.main",
                display: "flex",
                p: 1,
              }}
            >
              <PendingActionsIcon />
            </Box>
            <Typography variant="h6" fontWeight="bold">
              アップロード進捗
            </Typography>
          </Box>
          <IconButton onClick={() => setOpen(false)} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent dividers sx={{ p: { xs: 2, md: 3 } }}>
          {progresses.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2, textAlign: "center" }}>
              アップロード中のサービスはありません
            </Typography>
          ) : (
            <>
              {/* PC用: テーブル */}
              <TableContainer sx={{ display: { xs: "none", md: "block" } }}>
                <Table sx={{ width: "100%" }}>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: "text.secondary", fontWeight: "bold", width: "40%" }}>
                        サービス名
                      </TableCell>
                      <TableCell sx={{ color: "text.secondary", fontWeight: "bold", width: "35%" }}>
                        進捗状況
                      </TableCell>
                      <TableCell sx={{ color: "text.secondary", fontWeight: "bold", width: "25%" }}>
                        完了予測時刻
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {progresses.map((p) => (
                      <TableRow key={p.serviceName} hover>
                        <TableCell>
                          <Box sx={{ alignItems: "center", display: "flex", gap: 2 }}>
                            <Box sx={{ color: "primary.main" }}>
                              <InsertDriveFileIcon sx={{ fontSize: 32 }} />
                            </Box>
                            <Typography
                              variant="body2"
                              fontWeight="bold"
                              sx={{ wordBreak: "break-all" }}
                            >
                              {p.serviceName}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ alignItems: "center", display: "flex", gap: 2 }}>
                            <Box sx={{ flex: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={p.progressPercent}
                                sx={{ borderRadius: 4, height: 8 }}
                              />
                            </Box>
                            <Typography variant="body2" fontWeight="bold">
                              {p.progressPercent}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box
                            sx={{
                              alignItems: "center",
                              color: "text.secondary",
                              display: "flex",
                              gap: 1,
                            }}
                          >
                            <AccessTimeIcon fontSize="small" />
                            <Typography variant="body2">{p.estimatedCompletionTime}</Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* モバイル用: カード */}
              <Stack spacing={2} sx={{ display: { xs: "flex", md: "none" } }}>
                {progresses.map((p) => (
                  <Card key={p.serviceName} variant="outlined" sx={{ borderRadius: 2 }}>
                    <CardContent sx={{ p: 2 }}>
                      <Box sx={{ alignItems: "center", display: "flex", gap: 2, mb: 1.5 }}>
                        <Box sx={{ color: "primary.main", display: "flex" }}>
                          <InsertDriveFileIcon sx={{ fontSize: 28 }} />
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography
                            variant="body2"
                            fontWeight="bold"
                            sx={{ wordBreak: "break-all" }}
                          >
                            {p.serviceName}
                          </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ alignItems: "center", display: "flex", gap: 2 }}>
                        <Box sx={{ flex: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={p.progressPercent}
                            sx={{ borderRadius: 3, height: 6 }}
                          />
                        </Box>
                        <Typography variant="body2" fontWeight="bold">
                          {p.progressPercent}%
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          alignItems: "center",
                          color: "text.secondary",
                          display: "flex",
                          gap: 0.5,
                          mt: 0.5,
                        }}
                      >
                        <AccessTimeIcon sx={{ fontSize: 14 }} />
                        <Typography variant="caption">
                          完了予測時刻: {p.estimatedCompletionTime}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </>
          )}
        </DialogContent>

        <DialogActions sx={{ bgcolor: "background.soft", p: 2 }}>
          <Button startIcon={<RefreshIcon />}>更新</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
