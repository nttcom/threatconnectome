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
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import { DateTimePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { addHours, isBefore } from "date-fns";
import { useSnackbar } from "notistack";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { TFunction } from "i18next";
import { FetchBaseQueryError } from "@reduxjs/toolkit/query/react";
import { SerializedError } from "@reduxjs/toolkit";

// @ts-expect-error TS7016
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import {
  useCreatePTeamInvitationMutation,
  useDeleteInvitationMutation,
  useGetInvitationListQuery,
} from "../../services/tcApi";
import { errorToString } from "../../utils/func";
// @ts-expect-error TS7016
import { APIError } from "../../utils/APIError";

import type { PTeamInvitationResponse } from "../../../types/types.gen";

type Invitation = {
  id: string;
  link: string;
  limitCount: number | null | undefined;
  expiration: Date;
  usedCount: number;
};

type UsageMode = "unlimited" | "limited";

const formatExpiration = (date: Date | null): string => {
  if (!date) return "無期限";
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const hh = String(date.getHours()).padStart(2, "0");
  const mm = String(date.getMinutes()).padStart(2, "0");
  return `${m}月${d}日 ${hh}:${mm}まで`;
};

const tokenToLink = (token: string) =>
  `${window.location.origin}${import.meta.env.VITE_PUBLIC_URL}/pteam/join?token=${token}`;

type InvitationListViewProps = {
  pteamId: string;
  onCreateClick: () => void;
  onClose: () => void;
  t: TFunction;
};

function InvitationItem({
  inv,
  pteamId,
  t,
}: {
  inv: PTeamInvitationResponse;
  pteamId: string;
  t: TFunction;
}) {
  const [copied, setCopied] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const [deleteInvitation] = useDeleteInvitationMutation();

  const handleCopy = async () => {
    await navigator.clipboard.writeText(tokenToLink(inv.invitation_id)).catch(console.error);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDelete = async (invitationId: string) => {
    const onSuccess = () => {
      enqueueSnackbar(t("createInvitationSucceeded"), { variant: "success" });
    };
    const onError = (error: string | SerializedError | FetchBaseQueryError) => {
      enqueueSnackbar(t("createInvitationFailed", { error: errorToString(error) }), {
        variant: "error",
      });
    };
    await deleteInvitation({ path: { pteam_id: pteamId, invitation_id: invitationId } })
      .unwrap()
      .then(() => onSuccess())
      .catch((error) => onError(error));
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
        {tokenToLink(inv.invitation_id)}
      </Typography>
      <Box display="flex" alignItems="center" gap={2} mb={1}>
        <Box display="flex" alignItems="center" gap={0.5}>
          <PersonIcon fontSize="small" color="action" />
          <Typography variant="caption" color="text.secondary">
            {inv.limit_count == null ? "無制限" : `${inv.used_count}/${inv.limit_count}回`}
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={0.5}>
          <ScheduleIcon fontSize="small" color="action" />
          <Typography variant="caption" color="text.secondary">
            {formatExpiration(new Date(inv.expiration))}
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
        <Button
          size="small"
          variant="outlined"
          color="error"
          onClick={() => handleDelete(inv.invitation_id)}
        >
          無効化
        </Button>
      </Box>
    </Paper>
  );
}

function InvitationListView({ pteamId, onCreateClick, onClose, t }: InvitationListViewProps) {
  const skip = useSkipUntilAuthUserIsReady() || !pteamId;
  const {
    data: invitationsData,
    error: invitationsError,
    isLoading: invitationsIsLoading,
  } = useGetInvitationListQuery({ pteam_id: pteamId }, { skip });

  if (skip) return <></>;
  if (invitationsError)
    throw new APIError(errorToString(invitationsError), {
      api: "getInvitationList",
    });
  if (invitationsIsLoading) return <>{t("loading")}</>;

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
        {invitationsData && invitationsData.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" py={3}>
            有効な招待リンクはありません
          </Typography>
        ) : (
          invitationsData?.map((inv) => (
            <InvitationItem key={inv.invitation_id} inv={inv} pteamId={pteamId} t={t} />
          ))
        )}
      </DialogContent>
    </>
  );
}

type InvitationCreateFormProps = {
  onBack: () => void;
  onSuccessNavigate: () => void;
  onClose: () => void;
  onSetCreatedInv: (inv: Invitation) => void;
  pteamId: string;
  t: TFunction;
};

function InvitationCreateForm({
  onBack,
  onSuccessNavigate,
  onClose,
  onSetCreatedInv,
  pteamId,
  t,
}: InvitationCreateFormProps) {
  const [usageMode, setUsageMode] = useState<UsageMode>("unlimited");
  const [limitCount, setLimitCount] = useState(1);
  const [expiration, setExpiration] = useState<Date>(addHours(new Date(), 1));

  const { enqueueSnackbar } = useSnackbar();

  const [createPTeamInvitation] = useCreatePTeamInvitationMutation();

  const now = new Date();
  const isCreateDisabled = !isBefore(now, expiration);

  const handleCreate = async () => {
    const onSuccess = (data: PTeamInvitationResponse) => {
      enqueueSnackbar(t("createInvitationSucceeded"), { variant: "success" });
      onSetCreatedInv({
        id: data.invitation_id,
        link: tokenToLink(data.invitation_id),
        limitCount: data.limit_count,
        expiration: new Date(data.expiration),
        usedCount: data.used_count,
      });
      onSuccessNavigate();
    };
    const onError = (error: string | SerializedError | FetchBaseQueryError) => {
      enqueueSnackbar(t("createInvitationFailed", { error: errorToString(error) }), {
        variant: "error",
      });
    };
    const data = {
      expiration: expiration.toISOString(),
      limit_count: usageMode === "limited" ? limitCount : null,
    };
    await createPTeamInvitation({ path: { pteam_id: pteamId }, body: data })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
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
            </Box>
            <DateTimePicker
              format="yyyy/MM/dd HH:mm"
              minDateTime={now}
              value={expiration}
              onChange={(val) => val && setExpiration(val)}
              slotProps={{ textField: { size: "small", fullWidth: true, sx: { mt: 1 } } }}
            />
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
    await navigator.clipboard.writeText(tokenToLink(invitation.link)).catch(console.error);
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
  pteamId: string;
};

export function InvitationManageDialog({ pteamId }: Props) {
  const { t } = useTranslation("pteam", { keyPrefix: "InvitationManageDialog" });

  const [open, setOpen] = useState(false);
  const [view, setView] = useState<"list" | "create" | "success">("list");
  const [createdInv, setCreatedInv] = useState<Invitation | null>(null);

  const handleOpen = () => {
    setView("list");
    setOpen(true);
  };
  const handleClose = () => setOpen(false);

  return (
    <>
      <Button variant="contained" color="success" onClick={handleOpen}>
        招待管理
      </Button>
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
        {view === "list" && (
          <InvitationListView
            pteamId={pteamId}
            onCreateClick={() => setView("create")}
            onClose={handleClose}
            t={t}
          />
        )}
        {view === "create" && (
          <InvitationCreateForm
            onBack={() => setView("list")}
            onSuccessNavigate={() => setView("success")}
            onClose={handleClose}
            onSetCreatedInv={setCreatedInv}
            pteamId={pteamId}
            t={t}
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
