import {
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  ArrowBack as ArrowBackIcon,
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

type InvitationListViewProps = {
  invitations: Invitation[];
  onDelete: (id: string) => void;
  onCreateClick: () => void;
  onClose: () => void;
};

function InvitationItem({ inv, onDelete }: { inv: Invitation; onDelete: (id: string) => void }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(inv.link).catch(console.error);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Paper variant="outlined" sx={{ p: 2, mb: 1.5 }}>
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
            {inv.limitCount == null ? "無制限" : `${inv.usedCount}/${inv.limitCount}回`}
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
        <Tooltip open={copied} title="コピーしました！" placement="top">
          <Button
            size="small"
            variant="outlined"
            startIcon={<ContentCopyIcon />}
            onClick={handleCopy}
          >
            コピー
          </Button>
        </Tooltip>
        <Button size="small" variant="outlined" color="error" onClick={() => onDelete(inv.id)}>
          無効化
        </Button>
      </Box>
    </Paper>
  );
}

function InvitationListView({
  invitations,
  onDelete,
  onCreateClick,
  onClose,
}: InvitationListViewProps) {
  return (
    <>
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" gap={1}>
          <LinkIcon fontSize="small" color="primary" />
          <Typography variant="h6" fontWeight="bold">
            招待リンク管理
          </Typography>
          <Box flexGrow={1} />
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
      </DialogTitle>
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
          <Button variant="contained" size="small" startIcon={<AddIcon />} onClick={onCreateClick}>
            新規作成
          </Button>
        </Box>
        {invitations.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" py={3}>
            有効な招待リンクはありません
          </Typography>
        ) : (
          invitations.map((inv) => <InvitationItem key={inv.id} inv={inv} onDelete={onDelete} />)
        )}
      </DialogContent>
    </>
  );
}

type InvitationCreateFormProps = {
  onCreate: (invitation: Invitation) => void;
  onBack: () => void;
  onClose: () => void;
};

function InvitationCreateForm({ onCreate, onBack, onClose }: InvitationCreateFormProps) {
  const [usageMode, setUsageMode] = useState<UsageMode>("unlimited");
  const [limitCount, setLimitCount] = useState(1);
  const [expirationEnabled, setExpirationEnabled] = useState(false);
  const [expiration, setExpiration] = useState<Date>(addHours(new Date(), 24));

  const now = new Date();
  const isCreateDisabled = expirationEnabled && !isBefore(now, expiration);

  const handleCreate = () => {
    const newInv: Invitation = {
      id: String(Date.now()),
      link: `https://example.com/pteam/join?token=${Math.random().toString(36).slice(2, 10)}`,
      limitCount: usageMode === "limited" ? limitCount : null,
      expiration: expirationEnabled ? expiration : null,
      usedCount: 0,
    };
    onCreate(newInv);
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" gap={1}>
          <IconButton size="small" onClick={onBack}>
            <ArrowBackIcon fontSize="small" />
          </IconButton>
          <Typography variant="h6" fontWeight="bold">
            新しいリンクの作成
          </Typography>
          <Box flexGrow={1} />
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
      </DialogTitle>
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
  );
}

type InvitationSuccessViewProps = {
  invitation: Invitation;
  onBack: () => void;
  onClose: () => void;
};

function InvitationSuccessView({ invitation, onBack, onClose }: InvitationSuccessViewProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(invitation.link).catch(console.error);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" gap={1}>
          <CheckCircleIcon fontSize="small" color="success" />
          <Typography variant="h6" fontWeight="bold">
            リンクを作成しました
          </Typography>
          <Box flexGrow={1} />
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
      </DialogTitle>
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
          <Typography variant="body2" color="text.secondary">
            以下のリンクをコピーして共有してください
          </Typography>
          <OutlinedInput
            value={invitation.link}
            fullWidth
            readOnly
            size="small"
            endAdornment={
              <InputAdornment position="end">
                <Tooltip
                  open={copied}
                  title="コピーしました！"
                  placement="top"
                  disableFocusListener
                  disableHoverListener
                  disableTouchListener
                >
                  <Box>
                    <IconButton
                      size="small"
                      onClick={handleCopy}
                      sx={{ display: { xs: "inline-flex", sm: "none" } }}
                    >
                      <ContentCopyIcon fontSize="small" />
                    </IconButton>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<ContentCopyIcon />}
                      onClick={handleCopy}
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
                  {invitation.limitCount == null ? "無制限" : `${invitation.limitCount}回まで`}
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={0.5}>
                <ScheduleIcon fontSize="small" color="action" />
                <Typography variant="body2">{formatExpiration(invitation.expiration)}</Typography>
              </Box>
            </Box>
          </Paper>
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2, justifyContent: "center" }}>
        <Button variant="outlined" onClick={onBack}>
          管理リストに戻る
        </Button>
      </DialogActions>
    </>
  );
}

type Props = {
  initialInvitations?: Invitation[];
};

export function InvitationManageDialog({ initialInvitations = DUMMY_INVITATIONS }: Props) {
  const [open, setOpen] = useState(false);
  const [view, setView] = useState<"list" | "create" | "success">("list");
  const [invitations, setInvitations] = useState<Invitation[]>(initialInvitations);
  const [createdInv, setCreatedInv] = useState<Invitation | null>(null);

  const handleOpen = () => {
    setView("list");
    setOpen(true);
  };
  const handleClose = () => setOpen(false);

  const handleCreate = (inv: Invitation) => {
    setInvitations((prev) => [inv, ...prev]);
    setCreatedInv(inv);
    setView("success");
  };

  const handleDelete = (id: string) => {
    setInvitations((prev) => prev.filter((inv) => inv.id !== id));
  };

  return (
    <>
      <Button variant="contained" color="success" onClick={handleOpen}>
        招待管理
      </Button>
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
        {view === "list" && (
          <InvitationListView
            invitations={invitations}
            onDelete={handleDelete}
            onCreateClick={() => setView("create")}
            onClose={handleClose}
          />
        )}
        {view === "create" && (
          <InvitationCreateForm
            onCreate={handleCreate}
            onBack={() => setView("list")}
            onClose={handleClose}
          />
        )}
        {view === "success" && createdInv && (
          <InvitationSuccessView
            invitation={createdInv}
            onBack={() => setView("list")}
            onClose={handleClose}
          />
        )}
      </Dialog>
    </>
  );
}
