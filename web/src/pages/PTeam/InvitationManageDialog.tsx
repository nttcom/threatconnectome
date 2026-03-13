import {
  Add as AddIcon,
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Close as CloseIcon,
  ContentCopy as ContentCopyIcon,
  Link as LinkIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  InputAdornment,
  OutlinedInput,
  Paper,
  Switch,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { addHours, isBefore } from "date-fns";
import { useState } from "react";

type Invitation = {
  id: string;
  link: string;
  limitCount: number | null;
  expiration: Date | null;
  usedCount: number;
};

type UsageMode = "unlimited" | "limited";

// Dummy data for mock
const DUMMY_INVITATIONS: Invitation[] = [
  {
    id: "1",
    link: "https://example.com/pteam/join?token=xt7k9p2m",
    limitCount: null,
    expiration: null,
    usedCount: 0,
  },
  {
    id: "2",
    link: "https://example.com/pteam/join?token=b4v9m1zq",
    limitCount: 5,
    expiration: new Date(Date.now() + 1000 * 60 * 60 * 24),
    usedCount: 2,
  },
];

const formatExpiration = (date: Date | null): string => {
  if (!date) return "無期限";
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const hh = String(date.getHours()).padStart(2, "0");
  const mm = String(date.getMinutes()).padStart(2, "0");
  return `${m}月${d}日 ${hh}:${mm}まで`;
};

type Props = {
  initialInvitations?: Invitation[];
};

export function InvitationManageDialog({ initialInvitations = DUMMY_INVITATIONS }: Props) {
  const [open, setOpen] = useState(false);
  const [view, setView] = useState<"list" | "create" | "success">("list");
  const [invitations, setInvitations] = useState<Invitation[]>(initialInvitations);

  // create form
  const [usageMode, setUsageMode] = useState<UsageMode>("unlimited");
  const [limitCount, setLimitCount] = useState(1);
  const [expirationEnabled, setExpirationEnabled] = useState(false);
  const [expiration, setExpiration] = useState<Date>(addHours(new Date(), 24));

  // success
  const [createdInv, setCreatedInv] = useState<Invitation | null>(null);

  // copy tooltip
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleOpen = () => {
    setView("list");
    setOpen(true);
  };
  const handleClose = () => setOpen(false);

  const resetForm = () => {
    setUsageMode("unlimited");
    setLimitCount(1);
    setExpirationEnabled(false);
    setExpiration(addHours(new Date(), 24));
  };

  const handleCreate = () => {
    const newInv: Invitation = {
      id: String(Date.now()),
      link: `https://example.com/pteam/join?token=${Math.random().toString(36).slice(2, 10)}`,
      limitCount: usageMode === "limited" ? limitCount : null,
      expiration: expirationEnabled ? expiration : null,
      usedCount: 0,
    };
    setInvitations((prev) => [newInv, ...prev]);
    setCreatedInv(newInv);
    setView("success");
  };

  const handleDelete = (id: string) => {
    setInvitations((prev) => prev.filter((inv) => inv.id !== id));
  };

  const handleCopy = (id: string, link: string) => {
    navigator.clipboard.writeText(link);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const now = new Date();
  const isCreateDisabled = expirationEnabled && !isBefore(now, expiration);

  return (
    <>
      <Button variant="contained" color="success" onClick={handleOpen}>
        招待管理
      </Button>
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
        {/* Title */}
        <DialogTitle sx={{ pb: 1 }}>
          <Box display="flex" alignItems="center" gap={1}>
            {view === "list" && (
              <>
                <LinkIcon fontSize="small" color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  招待リンク管理
                </Typography>
              </>
            )}
            {view === "create" && (
              <>
                <IconButton
                  size="small"
                  onClick={() => {
                    setView("list");
                    resetForm();
                  }}
                >
                  <ArrowBackIcon fontSize="small" />
                </IconButton>
                <Typography variant="h6" fontWeight="bold">
                  新しいリンクの作成
                </Typography>
              </>
            )}
            {view === "success" && (
              <>
                <CheckCircleIcon fontSize="small" color="success" />
                <Typography variant="h6" fontWeight="bold">
                  リンクを作成しました
                </Typography>
              </>
            )}
            <Box flexGrow={1} />
            <IconButton size="small" onClick={handleClose}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        </DialogTitle>

        {/* List view */}
        {view === "list" && (
          <DialogContent>
            <Box
              display="flex"
              flexDirection={{ xs: "column", sm: "row" }}
              justifyContent="space-between"
              alignItems={{ xs: "flex-start", sm: "center" }}
              gap={1}
              mb={2}
            >
              <Typography variant="body2" color="text.secondary">
                発行済みのリンクを管理できます
              </Typography>
              <Button
                variant="contained"
                size="small"
                startIcon={<AddIcon />}
                onClick={() => {
                  resetForm();
                  setView("create");
                }}
              >
                新規作成
              </Button>
            </Box>
            {invitations.length === 0 ? (
              <Typography variant="body2" color="text.secondary" textAlign="center" py={3}>
                有効な招待リンクはありません
              </Typography>
            ) : (
              invitations.map((inv) => {
                return (
                  <Paper key={inv.id} variant="outlined" sx={{ p: 2, mb: 1.5 }}>
                    <Typography
                      variant="body2"
                      color="primary"
                      sx={{
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        mb: 0.5,
                      }}
                    >
                      {inv.link}
                    </Typography>
                    <Box display="flex" alignItems="center" gap={2} mb={1}>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <PersonIcon fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {inv.limitCount == null
                            ? "無制限"
                            : `${inv.usedCount}/${inv.limitCount}回`}
                        </Typography>
                      </Box>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <ScheduleIcon fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {formatExpiration(inv.expiration)}
                        </Typography>
                      </Box>
                    </Box>
                    <Box display="flex" justifyContent="flex-end" gap={1}>
                      <Tooltip open={copiedId === inv.id} title="コピーしました！" placement="top">
                        <Box>
                          <IconButton
                            size="small"
                            onClick={() => handleCopy(inv.id, inv.link)}
                            sx={{ display: { xs: "inline-flex", sm: "none" } }}
                          >
                            <ContentCopyIcon fontSize="small" />
                          </IconButton>
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<ContentCopyIcon />}
                            onClick={() => handleCopy(inv.id, inv.link)}
                            sx={{ display: { xs: "none", sm: "inline-flex" } }}
                          >
                            コピー
                          </Button>
                        </Box>
                      </Tooltip>
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        onClick={() => handleDelete(inv.id)}
                      >
                        無効化
                      </Button>
                    </Box>
                  </Paper>
                );
              })
            )}
          </DialogContent>
        )}

        {/* Create view */}
        {view === "create" && (
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DialogContent>
              <Paper variant="outlined" sx={{ p: 2 }}>
                {/* Usage limit */}
                <Box mb={3}>
                  <Box display="flex" alignItems="center" gap={0.5} mb={1}>
                    <PersonIcon fontSize="small" color="action" />
                    <Typography variant="body2" fontWeight="medium">
                      使用回数制限
                    </Typography>
                  </Box>
                  <ToggleButtonGroup
                    value={usageMode}
                    exclusive
                    onChange={(_, val: UsageMode | null) => val && setUsageMode(val)}
                    fullWidth
                    size="small"
                  >
                    <ToggleButton value="unlimited">無制限</ToggleButton>
                    <ToggleButton value="limited">回数を指定</ToggleButton>
                  </ToggleButtonGroup>
                  {usageMode === "limited" && (
                    <Box display="flex" alignItems="center" gap={1} mt={1.5}>
                      <TextField
                        type="number"
                        size="small"
                        value={limitCount}
                        onChange={(e) => setLimitCount(Math.max(1, Number(e.target.value)))}
                        slotProps={{ htmlInput: { min: 1 } }}
                        sx={{ width: 100 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        回まで使用可能
                      </Typography>
                    </Box>
                  )}
                </Box>

                {/* Expiration */}
                <Box>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <ScheduleIcon fontSize="small" color="action" />
                    <Typography variant="body2" fontWeight="medium">
                      有効期限
                    </Typography>
                    <Box flexGrow={1} />
                    <Switch
                      checked={expirationEnabled}
                      onChange={(e) => setExpirationEnabled(e.target.checked)}
                      size="small"
                    />
                  </Box>
                  {expirationEnabled ? (
                    <DateTimePicker
                      format="yyyy/MM/dd HH:mm"
                      minDateTime={now}
                      value={expiration}
                      onChange={(val) => val && setExpiration(val)}
                      slotProps={{ textField: { size: "small", fullWidth: true, sx: { mt: 1 } } }}
                    />
                  ) : (
                    <Typography variant="body2" color="text.secondary" mt={0.5}>
                      期限なし（いつでも使用可能）
                    </Typography>
                  )}
                </Box>
              </Paper>
            </DialogContent>
            <DialogActions sx={{ px: 3, pb: 2 }}>
              <Button variant="contained" onClick={handleCreate} disabled={isCreateDisabled}>
                リンクを作成
              </Button>
            </DialogActions>
          </LocalizationProvider>
        )}

        {/* Success view */}
        {view === "success" && createdInv && (
          <>
            <DialogContent>
              <Box display="flex" flexDirection="column" alignItems="center" gap={2} py={1}>
                <Box
                  sx={{
                    bgcolor: "success.light",
                    borderRadius: "50%",
                    width: 64,
                    height: 64,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <LinkIcon sx={{ color: "success.dark", fontSize: 32 }} />
                </Box>
                <Typography variant="h6" fontWeight="bold">
                  招待準備が完了しました
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  以下のリンクをコピーして共有してください
                </Typography>
                <OutlinedInput
                  value={createdInv.link}
                  fullWidth
                  readOnly
                  size="small"
                  endAdornment={
                    <InputAdornment position="end">
                      <Tooltip
                        open={copiedId === createdInv.id}
                        title="コピーしました！"
                        placement="top"
                        disableFocusListener
                        disableHoverListener
                        disableTouchListener
                      >
                        <Box>
                          <IconButton
                            size="small"
                            onClick={() => handleCopy(createdInv.id, createdInv.link)}
                            sx={{ display: { xs: "inline-flex", sm: "none" } }}
                          >
                            <ContentCopyIcon fontSize="small" />
                          </IconButton>
                          <Button
                            variant="contained"
                            size="small"
                            startIcon={<ContentCopyIcon />}
                            onClick={() => handleCopy(createdInv.id, createdInv.link)}
                            sx={{ display: { xs: "none", sm: "inline-flex" } }}
                          >
                            コピー
                          </Button>
                        </Box>
                      </Tooltip>
                    </InputAdornment>
                  }
                />
                <Paper variant="outlined" sx={{ width: "100%", p: 1.5 }}>
                  <Box display="flex" justifyContent="center" gap={3}>
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <PersonIcon fontSize="small" color="action" />
                      <Typography variant="body2">
                        {createdInv.limitCount == null
                          ? "無制限"
                          : `${createdInv.limitCount}回まで`}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center" gap={0.5}>
                      <ScheduleIcon fontSize="small" color="action" />
                      <Typography variant="body2">
                        {formatExpiration(createdInv.expiration)}
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              </Box>
            </DialogContent>
            <DialogActions sx={{ px: 3, pb: 2, justifyContent: "center" }}>
              <Button variant="outlined" onClick={() => setView("list")}>
                管理リストに戻る
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </>
  );
}
