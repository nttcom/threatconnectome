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
type ViewType = "list" | "create" | "success";

const formatExpiration = (date: Date | null, t: TFunction): string => {
  if (!date) return t("unlimitedExpiration");
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const hh = String(date.getHours()).padStart(2, "0");
  const mm = String(date.getMinutes()).padStart(2, "0");
  return t("expirationFormat", { m, d, hh, mm });
};

const tokenToLink = (token: string) =>
  `${window.location.origin}${import.meta.env.VITE_PUBLIC_URL}/pteam/join?token=${token}`;

const handleCopy = async (
  link: string,
  setCopied: React.Dispatch<React.SetStateAction<boolean>>,
) => {
  await navigator.clipboard.writeText(link).catch(console.error);
  setCopied(true);
  setTimeout(() => setCopied(false), 2000);
};

type InvitationItemProps = {
  inv: PTeamInvitationResponse;
  pteamId: string;
  t: TFunction;
};

function InvitationItem({ inv, pteamId, t }: InvitationItemProps) {
  const [copied, setCopied] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const [deleteInvitation] = useDeleteInvitationMutation();

  const handleDelete = async (invitationId: string) => {
    const onSuccess = () => {
      enqueueSnackbar(t("deleteInvitationSucceeded"), { variant: "success" });
    };
    const onError = (error: string | SerializedError | FetchBaseQueryError) => {
      enqueueSnackbar(t("deleteInvitationFailed", { error: errorToString(error) }), {
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
            {inv.limit_count == null
              ? t("unlimited")
              : t("usageCount", { used: inv.used_count, limit: inv.limit_count })}
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={0.5}>
          <ScheduleIcon fontSize="small" color="action" />
          <Typography variant="caption" color="text.secondary">
            {formatExpiration(new Date(inv.expiration), t)}
          </Typography>
        </Box>
      </Box>
      <Box display="flex" justifyContent="flex-end" gap={1}>
        <Tooltip open={copied} title={t("copied")} placement="top">
          <Button
            size="small"
            variant="outlined"
            startIcon={<ContentCopyIcon />}
            onClick={() => handleCopy(tokenToLink(inv.invitation_id), setCopied)}
          >
            {t("copy")}
          </Button>
        </Tooltip>
        <Button
          size="small"
          variant="outlined"
          color="error"
          onClick={() => handleDelete(inv.invitation_id)}
        >
          {t("deactivate")}
        </Button>
      </Box>
    </Paper>
  );
}

type InvitationListViewProps = {
  pteamId: string;
  onCreateClick: () => void;
  onClose: () => void;
  t: TFunction;
};

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
            {t("invitationLinkManagement")}
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
            {t("manageSentLinksDescription")}
          </Typography>
          <Button variant="contained" size="small" startIcon={<AddIcon />} onClick={onCreateClick}>
            {t("createNew")}
          </Button>
        </Box>
        {invitationsData && invitationsData.length === 0 ? (
          <Typography variant="body2" color="text.secondary" textAlign="center" py={3}>
            {t("noActiveInvitations")}
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
            {t("createNewLink")}
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
                {t("usageLimit")}
              </Typography>
            </Box>
            <ToggleButtonGroup
              value={usageMode}
              exclusive
              onChange={(_, val: UsageMode | null) => val && setUsageMode(val)}
              fullWidth
              size="small"
            >
              <ToggleButton value="unlimited">{t("unlimited")}</ToggleButton>
              <ToggleButton value="limited">{t("specifyCount")}</ToggleButton>
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
                  {t("usageCountSuffix")}
                </Typography>
              </Box>
            )}
          </Box>

          {/* Expiration */}
          <Box>
            <Box display="flex" alignItems="center" gap={0.5}>
              <ScheduleIcon fontSize="small" color="action" />
              <Typography variant="body2" fontWeight="medium">
                {t("expirationDate")}
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
          {t("createLink")}
        </Button>
      </DialogActions>
    </LocalizationProvider>
  );
}

type InvitationSuccessViewProps = {
  invitation: Invitation;
  onBack: () => void;
  onClose: () => void;
  t: TFunction;
};

function InvitationSuccessView({ invitation, onBack, onClose, t }: InvitationSuccessViewProps) {
  const [copied, setCopied] = useState(false);

  return (
    <>
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" gap={1}>
          <CheckCircleIcon fontSize="small" color="success" />
          <Typography variant="h6" fontWeight="bold">
            {t("linkCreatedSuccessfully")}
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
            {t("copyAndShareDescription")}
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
                      onClick={() => handleCopy(invitation.link, setCopied)}
                      sx={{ display: { xs: "inline-flex", sm: "none" } }}
                    >
                      <ContentCopyIcon fontSize="small" />
                    </IconButton>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<ContentCopyIcon />}
                      onClick={() => handleCopy(invitation.link, setCopied)}
                      sx={{ display: { xs: "none", sm: "inline-flex" } }}
                    >
                      {t("copy")}
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
                  {invitation.limitCount == null
                    ? t("unlimited")
                    : t("upToCount", { count: invitation.limitCount })}
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={0.5}>
                <ScheduleIcon fontSize="small" color="action" />
                <Typography variant="body2">
                  {formatExpiration(invitation.expiration, t)}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2, justifyContent: "center" }}>
        <Button variant="outlined" onClick={onBack}>
          {t("backToList")}
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
  const [view, setView] = useState<ViewType>("list");
  const [createdInv, setCreatedInv] = useState<Invitation | null>(null);

  const handleOpen = () => {
    setView("list");
    setOpen(true);
  };
  const handleClose = () => setOpen(false);

  return (
    <>
      <Button variant="contained" color="success" onClick={handleOpen}>
        {t("invitationManagement")}
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
            t={t}
          />
        )}
      </Dialog>
    </>
  );
}
