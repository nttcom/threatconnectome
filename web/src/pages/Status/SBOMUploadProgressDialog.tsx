import {
  AccessTime as AccessTimeIcon,
  Close as CloseIcon,
  InsertDriveFile as InsertDriveFileIcon,
  PendingActions as PendingActionsIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";
import {
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
  Typography,
} from "@mui/material";
import { useTranslation } from "react-i18next";

import type { SbomUploadProgressResponse } from "../../../types/types.gen";
import { utcStringToLocalDate } from "../../utils/func";

type Props = {
  progresses: SbomUploadProgressResponse[];
  open: boolean;
  setOpen: (open: boolean) => void;
  refetch: () => void;
};

export function SBOMUploadProgressDialog({ progresses, open, setOpen, refetch }: Props) {
  const { t } = useTranslation("status", { keyPrefix: "SBOMUploadProgressDialog" });

  return (
    <>
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
              {t("dialogTitle")}
            </Typography>
          </Box>
          <IconButton onClick={() => setOpen(false)} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent dividers sx={{ p: { xs: 2, md: 3 } }}>
          {progresses.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2, textAlign: "center" }}>
              {t("noServices")}
            </Typography>
          ) : (
            <>
              <TableContainer sx={{ display: { xs: "none", md: "block" } }}>
                <Table sx={{ width: "100%" }}>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: "text.secondary", fontWeight: "bold", width: "40%" }}>
                        {t("serviceName")}
                      </TableCell>
                      <TableCell sx={{ color: "text.secondary", fontWeight: "bold", width: "35%" }}>
                        {t("progressState")}
                      </TableCell>
                      <TableCell sx={{ color: "text.secondary", fontWeight: "bold", width: "25%" }}>
                        {t("expectedFinishTime")}
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {progresses.map((progress) => (
                      <TableRow key={progress.service_name} hover>
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
                              {progress.service_name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ alignItems: "center", display: "flex", gap: 2 }}>
                            <Box sx={{ flex: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={progress.progress_rate * 100}
                                sx={{ borderRadius: 4, height: 8 }}
                              />
                            </Box>
                            <Typography variant="body2" fontWeight="bold">
                              {progress.progress_rate * 100}%
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
                            <Typography variant="body2">
                              {utcStringToLocalDate(progress.expected_finish_time, false)}
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* For mobile */}
              <Stack spacing={2} sx={{ display: { xs: "flex", md: "none" } }}>
                {progresses.map((progress) => (
                  <Card key={progress.service_name} variant="outlined" sx={{ borderRadius: 2 }}>
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
                            {progress.service_name}
                          </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ alignItems: "center", display: "flex", gap: 2 }}>
                        <Box sx={{ flex: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={progress.progress_rate * 100}
                            sx={{ borderRadius: 3, height: 6 }}
                          />
                        </Box>
                        <Typography variant="body2" fontWeight="bold">
                          {progress.progress_rate * 100}%
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
                          {t("expectedFinishTime")}:{" "}
                          {utcStringToLocalDate(progress.expected_finish_time, false)}
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
          <Button startIcon={<RefreshIcon />} onClick={refetch}>
            {t("refresh")}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
