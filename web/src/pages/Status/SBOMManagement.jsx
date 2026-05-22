import { useEffect, useMemo, useRef, useState } from "react";
import AddIcon from "@mui/icons-material/Add";
import CheckIcon from "@mui/icons-material/Check";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import CloseIcon from "@mui/icons-material/Close";
import DeleteIcon from "@mui/icons-material/Delete";
import DescriptionIcon from "@mui/icons-material/Description";
import EditIcon from "@mui/icons-material/Edit";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ImageIcon from "@mui/icons-material/Image";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import LocalOfferIcon from "@mui/icons-material/LocalOffer";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import SearchIcon from "@mui/icons-material/Search";
import StorageRoundedIcon from "@mui/icons-material/StorageRounded";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogContent,
  IconButton,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import { SSVCPriorityStatusChip } from "../../components/SSVCPriorityStatusChip";
import {
  createDefaultSboms,
  createId,
  generateDependencies,
  getNextActiveIdAfterRemoval,
  isDeleteConfirmationValid,
  NEW_SBOM_ID,
  normalizeTags,
  parseDependenciesFromSbom,
} from "../../utils/sbomManagementUtils";

import { SBOMUpdateDialog } from "./SbomDrop/SBOMUpdateDialog";

const slate = {
  50: "#f8fafc",
  100: "#f1f5f9",
  200: "#e2e8f0",
  300: "#cbd5e1",
  400: "#94a3b8",
  500: "#64748b",
  600: "#475569",
  700: "#334155",
  800: "#1e293b",
  900: "#0f172a",
  950: "#020617",
};

const fieldSx = {
  "& .MuiOutlinedInput-root": {
    backgroundColor: "white",
    borderRadius: 4,
    boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
    fontSize: 14,
  },
};

const labelSx = {
  color: slate[500],
  fontSize: 12,
  fontWeight: 700,
  letterSpacing: 0,
  textTransform: "uppercase",
};

const textButtonSx = {
  "& .MuiButton-endIcon": { ml: 0.75 },
  "& .MuiButton-startIcon": { mr: 0.75 },
  borderRadius: 3,
  fontWeight: 600,
  lineHeight: 1,
  textTransform: "none",
  whiteSpace: "nowrap",
};

const compactSelectSx = {
  "& .MuiSelect-select": {
    alignItems: "center",
    display: "flex",
    minHeight: 0,
    py: 0,
  },
  borderRadius: 3,
  color: slate[700],
  fontSize: 13,
  height: 32,
  minWidth: 72,
};

const sectionIconBoxSx = {
  alignItems: "center",
  color: slate[700],
  display: "flex",
  flexShrink: 0,
  height: 20,
  justifyContent: "center",
  lineHeight: 0,
  width: 20,
};

const sectionTitleTextSx = {
  color: slate[700],
  display: "block",
  fontSize: 16,
  fontWeight: 700,
  letterSpacing: 0,
  lineHeight: "20px",
};

function CountBadge({ children }) {
  return (
    <Box
      component="span"
      sx={{
        alignItems: "center",
        bgcolor: slate[100],
        borderRadius: 999,
        color: slate[600],
        display: "inline-flex",
        flexShrink: 0,
        fontSize: 12,
        fontWeight: 700,
        height: 32,
        justifyContent: "center",
        lineHeight: 1,
        px: 1.25,
      }}
    >
      {children}
    </Box>
  );
}

function HeaderActionButton({ active = false, children, icon: Icon, sx, ...props }) {
  return (
    <Box
      component="button"
      type="button"
      sx={{
        "&:disabled": {
          cursor: "default",
          opacity: 0.5,
        },
        alignItems: "center",
        bgcolor: active ? slate[950] : "white",
        border: `1px solid ${active ? slate[950] : slate[300]}`,
        borderRadius: 999,
        color: active ? "white" : slate[900],
        cursor: "pointer",
        display: "inline-flex",
        flexShrink: 0,
        font: "inherit",
        fontSize: 13,
        fontWeight: 700,
        gap: 0.75,
        height: 32,
        justifyContent: "center",
        lineHeight: 1,
        minWidth: 0,
        px: 1.5,
        whiteSpace: "nowrap",
        ...sx,
      }}
      {...props}
    >
      {Icon && <Icon sx={{ display: "block", fontSize: 18, height: 18, width: 18 }} />}
      <Box component="span" sx={{ display: "block", lineHeight: 1 }}>
        {children}
      </Box>
    </Box>
  );
}

function AppButton({ size = "medium", sx, variant = "contained", ...props }) {
  const muiSize = size === "xs" || size === "sm" ? "small" : size;

  return (
    <Button
      size={muiSize}
      sx={{
        ...textButtonSx,
        height: size === "xs" ? 32 : muiSize === "small" ? 34 : 40,
        minHeight: size === "xs" ? 32 : muiSize === "small" ? 34 : 40,
        px: size === "xs" ? 1.25 : muiSize === "small" ? 1.5 : 2,
        ...sx,
      }}
      variant={variant}
      {...props}
    />
  );
}

function TabButton({ active, onClick, sbom }) {
  return (
    <Box
      component="button"
      onClick={onClick}
      sx={{
        "&:hover": {
          backgroundColor: active ? "white" : slate[200],
          color: active ? slate[950] : slate[800],
        },
        backgroundColor: active ? "white" : slate[100],
        border: "1px solid",
        borderColor: active ? slate[200] : "transparent",
        borderTopLeftRadius: 16,
        borderTopRightRadius: 16,
        boxShadow: active ? "0 1px 2px rgba(15, 23, 42, 0.05)" : "none",
        color: active ? slate[950] : slate[500],
        cursor: "pointer",
        font: "inherit",
        fontSize: 14,
        fontWeight: 600,
        px: 2.5,
        py: 1.5,
        transition: "background-color 160ms ease, color 160ms ease, border-color 160ms ease",
        whiteSpace: "nowrap",
      }}
      type="button"
    >
      {sbom.title || "Untitled SBOM"}
    </Box>
  );
}

function AccordionHeader({ action, icon: Icon, onToggle, open, title }) {
  return (
    <Box sx={{ alignItems: "center", display: "flex", gap: 1.5, height: 44, px: 2 }}>
      <Box
        component="button"
        onClick={onToggle}
        sx={{
          alignItems: "center",
          background: "transparent",
          border: 0,
          color: "inherit",
          cursor: "pointer",
          display: "flex",
          flex: "1 1 auto",
          font: "inherit",
          gap: 1,
          height: 32,
          minWidth: 0,
          p: 0,
          pointerEvents: { md: "none" },
          textAlign: "left",
        }}
        type="button"
      >
        <Stack direction="row" alignItems="center" sx={{ gap: 1, height: 32, minWidth: 0 }}>
          <Box sx={{ ...sectionIconBoxSx, height: 32 }}>
            <Icon sx={{ display: "block", fontSize: 18, height: 18, width: 18 }} />
          </Box>
          <Typography
            noWrap
            sx={{
              ...sectionTitleTextSx,
              alignItems: "center",
              display: "inline-flex",
              height: 32,
              lineHeight: 1,
            }}
          >
            {title}
          </Typography>
        </Stack>
        <ExpandMoreIcon
          sx={{
            color: slate[400],
            display: { md: "none", xs: "block" },
            flexShrink: 0,
            fontSize: 22,
            height: 22,
            ml: "auto",
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 160ms ease",
            width: 22,
          }}
        />
      </Box>
      <Box
        sx={{
          alignItems: "center",
          display: "flex",
          flexShrink: 0,
          height: 32,
          justifyContent: "flex-end",
          minWidth: 0,
        }}
      >
        {action}
      </Box>
    </Box>
  );
}

function SbomImage({ editing, imageUrl, onImageUpload, onRemoveImage, title }) {
  const [confirmingRemove, setConfirmingRemove] = useState(false);
  const imageInputRef = useRef(null);

  const openImagePicker = () => {
    setConfirmingRemove(false);
    imageInputRef.current?.click();
  };

  const imageInput = (
    <Box
      accept="image/*"
      component="input"
      onChange={onImageUpload}
      ref={imageInputRef}
      sx={{ display: "none" }}
      type="file"
    />
  );

  if (!imageUrl) {
    return (
      <Box
        sx={{
          alignItems: "center",
          bgcolor: slate[50],
          borderBottom: `1px dashed ${slate[300]}`,
          color: slate[400],
          display: "flex",
          height: 192,
          justifyContent: "center",
          position: "relative",
        }}
      >
        {imageInput}
        <Box sx={{ textAlign: "center" }}>
          <ImageIcon sx={{ fontSize: 32, mb: 1 }} />
          <Typography sx={{ fontSize: 14 }}>イメージ画像が未設定です</Typography>
          {editing && (
            <AppButton
              onClick={openImagePicker}
              size="small"
              startIcon={<UploadFileIcon />}
              sx={{ bgcolor: "white", mt: 1.5 }}
              variant="outlined"
            >
              画像をアップロード
            </AppButton>
          )}
        </Box>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        borderBottom: `1px solid ${slate[200]}`,
        height: 192,
        overflow: "hidden",
        position: "relative",
      }}
    >
      {imageInput}
      <Box
        alt={title || "SBOM Image"}
        component="img"
        src={imageUrl}
        sx={{ height: "100%", objectFit: "cover", width: "100%" }}
      />
      <Box
        sx={{
          background: "linear-gradient(to top, rgba(0,0,0,0.45), rgba(0,0,0,0.1), transparent)",
          inset: 0,
          position: "absolute",
        }}
      />

      {editing && !confirmingRemove && (
        <Stack
          direction="row"
          flexWrap="wrap"
          justifyContent="flex-end"
          sx={{ gap: 1, position: "absolute", right: 12, top: 12 }}
        >
          <AppButton
            onClick={openImagePicker}
            size="small"
            startIcon={<UploadFileIcon />}
            sx={{ bgcolor: "rgba(255,255,255,0.95)" }}
            variant="outlined"
          >
            画像を変更
          </AppButton>
          <AppButton
            onClick={() => setConfirmingRemove(true)}
            size="small"
            startIcon={<DeleteIcon />}
            sx={{ bgcolor: "rgba(255,255,255,0.95)", color: slate[700] }}
            variant="outlined"
          >
            削除
          </AppButton>
        </Stack>
      )}

      {confirmingRemove && (
        <Box
          sx={{
            bgcolor: "white",
            border: `1px solid ${slate[200]}`,
            borderRadius: 4,
            boxShadow: "0 10px 15px rgba(15, 23, 42, 0.1)",
            left: 12,
            p: 1.5,
            position: "absolute",
            right: 12,
            top: 12,
            zIndex: 1,
          }}
        >
          <Typography sx={{ color: slate[800], fontSize: 14, fontWeight: 700 }}>
            画像を削除しますか？
          </Typography>
          <Typography sx={{ color: slate[500], fontSize: 12, lineHeight: "20px", mt: 0.5 }}>
            削除すると未設定の状態に戻ります。
          </Typography>
          <Stack direction="row" sx={{ gap: 1, mt: 1.5 }}>
            <AppButton
              onClick={() => setConfirmingRemove(false)}
              size="small"
              sx={{ flex: 1 }}
              variant="outlined"
            >
              キャンセル
            </AppButton>
            <AppButton
              onClick={() => {
                onRemoveImage();
                setConfirmingRemove(false);
              }}
              size="small"
              sx={{ flex: 1 }}
            >
              削除する
            </AppButton>
          </Stack>
        </Box>
      )}

      <Box sx={{ bottom: 16, left: 16, position: "absolute", right: 16 }}>
        <Typography
          sx={{
            color: "rgba(255,255,255,0.7)",
            fontSize: 12,
            fontWeight: 600,
            textTransform: "uppercase",
          }}
        >
          イメージ
        </Typography>
        <Typography noWrap sx={{ color: "white", fontSize: 16, fontWeight: 700, mt: 0.5 }}>
          {title || "Untitled SBOM"}
        </Typography>
      </Box>
    </Box>
  );
}

function DetailsForm({ editing, onUpdate, open, sbom }) {
  const emptyText = (
    <Box component="span" sx={{ color: slate[400] }}>
      未設定
    </Box>
  );
  const display = { md: "block", xs: open ? "block" : "none" };

  if (!editing) {
    return (
      <Stack sx={{ display, gap: 2 }}>
        <Box>
          <Typography sx={labelSx}>タイトル</Typography>
          <Typography sx={{ color: slate[800], fontSize: 14, fontWeight: 700, mt: 0.75 }}>
            {sbom.title || emptyText}
          </Typography>
        </Box>
        <Box>
          <Typography sx={labelSx}>説明文</Typography>
          <Typography
            sx={{
              color: slate[700],
              fontSize: 14,
              lineHeight: "24px",
              mt: 0.75,
              whiteSpace: "pre-wrap",
            }}
          >
            {sbom.description || emptyText}
          </Typography>
        </Box>
        <Box>
          <Typography sx={labelSx}>タグ</Typography>
          {sbom.tags.length > 0 ? (
            <Stack direction="row" flexWrap="wrap" sx={{ gap: 1, mt: 1 }}>
              {sbom.tags.map((tag) => (
                <Chip
                  icon={<LocalOfferIcon />}
                  key={tag}
                  label={tag}
                  size="small"
                  sx={{ bgcolor: slate[100], color: slate[600], fontSize: 12, fontWeight: 600 }}
                />
              ))}
            </Stack>
          ) : (
            <Typography sx={{ color: slate[400], fontSize: 14, mt: 1 }}>未設定</Typography>
          )}
        </Box>
      </Stack>
    );
  }

  return (
    <Stack sx={{ display, gap: 2 }}>
      <Box>
        <Typography component="label" sx={labelSx}>
          タイトル
        </Typography>
        <TextField
          fullWidth
          onChange={(event) => onUpdate({ title: event.target.value })}
          placeholder="例: Payment Service SBOM"
          sx={{ ...fieldSx, mt: 1 }}
          value={sbom.title}
        />
      </Box>
      <Box>
        <Typography component="label" sx={labelSx}>
          説明文
        </Typography>
        <TextField
          fullWidth
          minRows={4}
          multiline
          onChange={(event) => onUpdate({ description: event.target.value })}
          placeholder="SBOMの対象システムや用途を入力"
          sx={{ ...fieldSx, mt: 1 }}
          value={sbom.description}
        />
      </Box>
      <Box>
        <Typography component="label" sx={labelSx}>
          タグ
        </Typography>
        <TextField
          fullWidth
          onChange={(event) => onUpdate({ tags: normalizeTags(event.target.value) })}
          placeholder="backend, prod, critical"
          sx={{ ...fieldSx, mt: 1 }}
          value={sbom.tags.join(", ")}
        />
      </Box>
    </Stack>
  );
}

function DeploymentList({ deployments, editing, onRemove, onUpdate, open }) {
  const display = { md: "block", xs: open ? "block" : "none" };

  return (
    <CardContent sx={{ display, minWidth: 0, pb: 1.5, pt: 0, px: 2 }}>
      <Stack sx={{ gap: 1.5 }}>
        {deployments.length > 0 ? (
          deployments.map((deployment, index) => (
            <Box
              key={deployment.id}
              sx={{
                bgcolor: slate[50],
                border: `1px solid ${slate[200]}`,
                borderRadius: 4,
                p: 1.5,
              }}
            >
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                sx={{ mb: 1.25 }}
              >
                <Typography sx={{ color: slate[700], fontSize: 14, fontWeight: 700 }}>
                  デプロイ先 {index + 1}
                </Typography>
                {editing && (
                  <IconButton
                    aria-label="デプロイ先を削除"
                    onClick={() => onRemove(deployment.id)}
                    size="small"
                    sx={{ color: slate[400], "&:hover": { bgcolor: "white", color: slate[900] } }}
                  >
                    <CloseIcon sx={{ fontSize: 18 }} />
                  </IconButton>
                )}
              </Stack>
              {editing ? (
                <Stack sx={{ gap: 1.25 }}>
                  <TextField
                    fullWidth
                    onChange={(event) => onUpdate(deployment.id, { ip: event.target.value })}
                    placeholder="IPアドレス"
                    sx={fieldSx}
                    value={deployment.ip}
                  />
                  <TextField
                    fullWidth
                    onChange={(event) => onUpdate(deployment.id, { location: event.target.value })}
                    placeholder="ロケーション"
                    sx={fieldSx}
                    value={deployment.location}
                  />
                </Stack>
              ) : (
                <Stack sx={{ gap: 1.25 }}>
                  <Box>
                    <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
                      IPアドレス
                    </Typography>
                    <Typography sx={{ color: slate[800], fontSize: 14, fontWeight: 600, mt: 0.5 }}>
                      {deployment.ip || (
                        <Box component="span" sx={{ color: slate[400] }}>
                          未設定
                        </Box>
                      )}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
                      ロケーション
                    </Typography>
                    <Stack
                      direction="row"
                      alignItems="center"
                      sx={{ color: slate[800], fontSize: 14, fontWeight: 600, gap: 1, mt: 0.5 }}
                    >
                      <LocationOnIcon sx={{ color: slate[400], fontSize: 18 }} />
                      <Typography
                        component="span"
                        sx={{ color: "inherit", fontSize: 14, fontWeight: 600 }}
                      >
                        {deployment.location || (
                          <Box component="span" sx={{ color: slate[400] }}>
                            未設定
                          </Box>
                        )}
                      </Typography>
                    </Stack>
                  </Box>
                </Stack>
              )}
            </Box>
          ))
        ) : (
          <Box
            sx={{
              border: `1px dashed ${slate[300]}`,
              borderRadius: 4,
              color: slate[500],
              fontSize: 14,
              p: 2.5,
              textAlign: "center",
            }}
          >
            デプロイ先が未登録です。
          </Box>
        )}
      </Stack>
    </CardContent>
  );
}

function DangerZone({ disabled = false, onDelete, onToggle, open, sbomTitle }) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirmationName, setConfirmationName] = useState("");
  const expectedName = sbomTitle || "Untitled SBOM";
  const canDelete = isDeleteConfirmationValid(confirmationName, expectedName);

  const closeDialog = () => {
    setDialogOpen(false);
    setConfirmationName("");
  };

  return (
    <Card
      sx={{
        bgcolor: slate[50],
        border: `1px solid ${slate[200]}`,
        borderRadius: 6,
        boxShadow: "none",
        minWidth: 0,
      }}
    >
      <Box
        component="button"
        onClick={() => {
          if (open) {
            closeDialog();
          }
          onToggle();
        }}
        sx={{
          alignItems: "center",
          background: "transparent",
          border: 0,
          cursor: "pointer",
          display: "flex",
          font: "inherit",
          justifyContent: "space-between",
          px: 2,
          py: 1.25,
          textAlign: "left",
          width: "100%",
        }}
        type="button"
      >
        <Stack direction="row" alignItems="center" sx={{ gap: 1, minHeight: 20 }}>
          <Box sx={sectionIconBoxSx}>
            <WarningAmberIcon sx={{ display: "block", fontSize: 18, height: 18, width: 18 }} />
          </Box>
          <Typography sx={sectionTitleTextSx}>危険操作</Typography>
        </Stack>
        <ExpandMoreIcon
          sx={{
            color: slate[400],
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 160ms ease",
          }}
        />
      </Box>

      {open && (
        <CardContent sx={{ pb: 1.5, pt: 0, px: 2 }}>
          <Stack sx={{ gap: 1.5 }}>
            <Typography sx={{ color: slate[500], fontSize: 14, lineHeight: "24px" }}>
              現在開いているSBOMタブを削除します。
            </Typography>
            <AppButton
              disabled={disabled}
              onClick={() => setDialogOpen(true)}
              startIcon={<DeleteIcon />}
              sx={{ bgcolor: "white", color: slate[700], width: "100%" }}
              variant="outlined"
            >
              削除ダイアログを開く
            </AppButton>
          </Stack>
        </CardContent>
      )}

      <Dialog
        fullWidth
        maxWidth="xs"
        onClose={closeDialog}
        open={dialogOpen}
        PaperProps={{ sx: { borderRadius: 6, p: 1 } }}
      >
        <DialogContent sx={{ p: 2, position: "relative" }}>
          <Box sx={{ pr: 6 }}>
            <Typography sx={{ color: slate[950], fontSize: 18, fontWeight: 800 }}>
              SBOMを削除
            </Typography>
          </Box>
          <IconButton
            aria-label="閉じる"
            onClick={closeDialog}
            size="small"
            sx={{
              "&:hover": { bgcolor: slate[100], color: slate[900] },
              color: slate[400],
              height: 32,
              p: 0,
              position: "absolute",
              right: 16,
              top: 16,
              width: 32,
            }}
          >
            <CloseIcon sx={{ fontSize: 20 }} />
          </IconButton>
          <Box sx={{ bgcolor: slate[50], borderRadius: 4, mt: 2.5, p: 2 }}>
            <Typography sx={labelSx}>削除対象</Typography>
            <Typography
              sx={{
                color: slate[800],
                fontSize: 14,
                fontWeight: 700,
                mt: 0.5,
                overflowWrap: "anywhere",
              }}
            >
              {expectedName}
            </Typography>
          </Box>
          <Box sx={{ mt: 2.5 }}>
            <Typography component="label" sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
              SBOM名を入力
            </Typography>
            <TextField
              autoFocus
              fullWidth
              onChange={(event) => setConfirmationName(event.target.value)}
              placeholder={expectedName}
              sx={{ ...fieldSx, mt: 1 }}
              value={confirmationName}
            />
            <Typography sx={{ color: slate[400], fontSize: 12, mt: 1 }}>
              削除対象のSBOM名を完全一致で入力してください。
            </Typography>
          </Box>
          <Box
            sx={{
              display: "grid",
              gap: 1,
              gridTemplateColumns: { sm: "1fr 1fr", xs: "1fr" },
              mt: 3,
            }}
          >
            <AppButton onClick={closeDialog} variant="outlined">
              キャンセル
            </AppButton>
            <AppButton
              disabled={!canDelete || disabled}
              onClick={() => {
                if (!canDelete || disabled) {
                  return;
                }
                onDelete();
                closeDialog();
              }}
              startIcon={<DeleteIcon />}
            >
              削除する
            </AppButton>
          </Box>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

function DependencyTable({ dependencies, onPackageClick, pageStartIndex }) {
  if (dependencies.length === 0) {
    return (
      <Box sx={{ p: 5, textAlign: "center" }}>
        <DescriptionIcon sx={{ color: slate[300], fontSize: 36, mb: 1.5 }} />
        <Typography sx={{ color: slate[600], fontSize: 14, fontWeight: 600 }}>
          依存関係がありません
        </Typography>
        <Typography sx={{ color: slate[400], fontSize: 12, mt: 0.5 }}>
          SBOM JSONをアップロードするか、検索条件を変更してください。
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {dependencies.map((dependency, index) => {
        const canNavigate = Boolean(onPackageClick && dependency.packageId && dependency.serviceId);
        const handleNavigate = () => {
          if (!canNavigate) {
            return;
          }
          onPackageClick(dependency.serviceId, dependency.packageId);
        };

        return (
          <Box
            key={`${dependency.name}-${dependency.version}-${pageStartIndex + index}`}
            onClick={handleNavigate}
            onKeyDown={(event) => {
              if (canNavigate && (event.key === "Enter" || event.key === " ")) {
                event.preventDefault();
                handleNavigate();
              }
            }}
            role={canNavigate ? "button" : undefined}
            tabIndex={canNavigate ? 0 : undefined}
            sx={{
              "&:hover": { bgcolor: slate[50] },
              alignItems: "center",
              borderTop: index === 0 ? 0 : `1px solid ${slate[100]}`,
              cursor: canNavigate ? "pointer" : "default",
              display: "grid",
              fontSize: 14,
              gridTemplateColumns: "48px 1.4fr 0.7fr 0.65fr 0.8fr",
              px: 2,
              py: 1.5,
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center" }}>
              {dependency.ssvcPriority && (
                <SSVCPriorityStatusChip displaySSVCPriority={dependency.ssvcPriority} />
              )}
            </Box>
            <Typography
              noWrap
              sx={{ color: slate[800], fontSize: 14, fontWeight: 700, minWidth: 0 }}
            >
              {dependency.name}
            </Typography>
            <Typography noWrap sx={{ color: slate[600], fontSize: 14 }}>
              {dependency.version || "-"}
            </Typography>
            <Box>
              <Chip
                label={dependency.type}
                size="small"
                sx={{ bgcolor: slate[100], color: slate[600], fontSize: 12, fontWeight: 600 }}
              />
            </Box>
            <Typography noWrap sx={{ color: slate[600], fontSize: 14 }}>
              {dependency.license || "-"}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
}

function NewSbomRegistrationPanel({ inputRef, onCancel, onFileChange, showCancel = true }) {
  return (
    <Box
      sx={{
        bgcolor: "white",
        borderBottomLeftRadius: 24,
        borderBottomRightRadius: 24,
        borderTopRightRadius: 24,
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
        p: { sm: 4, xs: 2 },
      }}
    >
      <Card
        sx={{
          border: `1px solid ${slate[200]}`,
          borderRadius: 6,
          boxShadow: "none",
          maxWidth: 768,
          mx: "auto",
          overflow: "hidden",
        }}
      >
        <Box sx={{ bgcolor: slate[50], px: { sm: 5, xs: 3 }, py: 5, textAlign: "center" }}>
          <Box
            sx={{
              alignItems: "center",
              bgcolor: "white",
              borderRadius: 6,
              boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
              display: "flex",
              height: 64,
              justifyContent: "center",
              mb: 2.5,
              mx: "auto",
              width: 64,
            }}
          >
            <DescriptionIcon sx={{ color: slate[500], fontSize: 32 }} />
          </Box>
          <Typography
            component="h2"
            sx={{ color: slate[950], fontSize: 24, fontWeight: 800, letterSpacing: 0 }}
          >
            新しいSBOMを登録
          </Typography>
          <Typography
            sx={{
              color: slate[600],
              fontSize: 14,
              lineHeight: "24px",
              maxWidth: 576,
              mt: 1.5,
              mx: "auto",
            }}
          >
            まずSBOM
            JSONをアップロードしてください。読み込み後に詳細情報とデプロイ先を設定できます。
          </Typography>
        </Box>
        <CardContent sx={{ p: { sm: 4, xs: 3 } }}>
          <Stack sx={{ gap: 2.5 }}>
            <Box
              accept=".json,application/json"
              component="input"
              onChange={onFileChange}
              ref={inputRef}
              sx={{ display: "none" }}
              type="file"
            />
            <Box
              component="button"
              onClick={() => inputRef.current?.click()}
              sx={{
                "&:hover": { bgcolor: "white", borderColor: slate[400] },
                alignItems: "center",
                bgcolor: slate[50],
                border: `1px dashed ${slate[300]}`,
                borderRadius: 6,
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                font: "inherit",
                justifyContent: "center",
                px: 3,
                py: 5,
                textAlign: "center",
                transition: "background-color 160ms ease, border-color 160ms ease",
                width: "100%",
              }}
              type="button"
            >
              <UploadFileIcon sx={{ color: slate[400], fontSize: 32, mb: 1.5 }} />
              <Typography
                component="span"
                sx={{ color: slate[800], fontSize: 14, fontWeight: 700 }}
              >
                最初のSBOMをアップロード
              </Typography>
              <Typography component="span" sx={{ color: slate[500], fontSize: 12, mt: 0.5 }}>
                CycloneDX JSON / SPDX JSON
              </Typography>
            </Box>
            {showCancel && (
              <Box sx={{ display: "flex", justifyContent: "center" }}>
                <AppButton onClick={onCancel} variant="outlined">
                  キャンセル
                </AppButton>
              </Box>
            )}
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}

export function SBOMManagement({
  initialActiveId,
  initialSboms = createDefaultSboms(),
  onPackageClick,
  pteamId,
}) {
  const [sboms, setSboms] = useState(initialSboms);
  const [activeId, setActiveId] = useState(initialActiveId || initialSboms[0]?.id || NEW_SBOM_ID);

  useEffect(() => {
    setSboms(initialSboms);
  }, [initialSboms]);
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [detailsEditing, setDetailsEditing] = useState(false);
  const [deploymentsOpen, setDeploymentsOpen] = useState(false);
  const [deploymentsEditing, setDeploymentsEditing] = useState(false);
  const [dangerOpen, setDangerOpen] = useState(false);
  const fileInputRef = useRef(null);
  const createFileInputRef = useRef(null);
  const [pendingUpload, setPendingUpload] = useState(null);

  const isEmpty = sboms.length === 0;
  const isCreatingSbom = activeId === NEW_SBOM_ID || isEmpty;
  const activeSbom = useMemo(() => {
    if (isCreatingSbom) {
      return null;
    }

    return sboms.find((sbom) => sbom.id === activeId) || sboms[0] || null;
  }, [activeId, isCreatingSbom, sboms]);

  const filteredDependencies = useMemo(() => {
    const target = query.trim().toLowerCase();

    if (!activeSbom) {
      return [];
    }

    if (!target) {
      return activeSbom.dependencies;
    }

    return activeSbom.dependencies.filter((dependency) =>
      [dependency.name, dependency.version, dependency.type, dependency.license]
        .join(" ")
        .toLowerCase()
        .includes(target),
    );
  }, [activeSbom, query]);

  const totalPages = Math.max(1, Math.ceil(filteredDependencies.length / pageSize));
  const safeCurrentPage = Math.min(currentPage, totalPages);
  const pageStartIndex = (safeCurrentPage - 1) * pageSize;
  const pageEndIndex = Math.min(pageStartIndex + pageSize, filteredDependencies.length);
  const paginatedDependencies = filteredDependencies.slice(pageStartIndex, pageEndIndex);

  const updateActiveSbom = (patch) => {
    setSboms((current) =>
      current.map((sbom) => (sbom.id === activeId ? { ...sbom, ...patch } : sbom)),
    );
  };

  const resetUiState = () => {
    setCurrentPage(1);
    setDangerOpen(false);
    setDeploymentsEditing(false);
    setDetailsEditing(false);
    setQuery("");
  };

  const addSbom = () => {
    setActiveId(NEW_SBOM_ID);
    setDeploymentsOpen(false);
    setDetailsOpen(false);
    resetUiState();
  };

  const cancelCreateSbom = () => {
    setActiveId(sboms[0]?.id || NEW_SBOM_ID);
    resetUiState();
  };

  const removeActiveSbom = () => {
    if (isCreatingSbom) {
      return;
    }

    const nextActiveId = getNextActiveIdAfterRemoval(sboms, activeId) || NEW_SBOM_ID;

    setSboms((current) => current.filter((sbom) => sbom.id !== activeId));
    setActiveId(nextActiveId);
    resetUiState();
  };

  const addDeployment = () => {
    if (!activeSbom) {
      return;
    }

    updateActiveSbom({
      deployments: [...activeSbom.deployments, { id: createId("dep"), ip: "", location: "" }],
    });
  };

  const updateDeployment = (deploymentId, patch) => {
    if (!activeSbom) {
      return;
    }

    updateActiveSbom({
      deployments: activeSbom.deployments.map((deployment) =>
        deployment.id === deploymentId ? { ...deployment, ...patch } : deployment,
      ),
    });
  };

  const removeDeployment = (deploymentId) => {
    if (!activeSbom) {
      return;
    }

    const confirmed =
      typeof window === "undefined" ||
      window.confirm("このデプロイ先を削除します。よろしいですか？");

    if (!confirmed) {
      return;
    }

    updateActiveSbom({
      deployments: activeSbom.deployments.filter((deployment) => deployment.id !== deploymentId),
    });
  };

  const readSbomFile = async (file) => {
    const text = await file.text();
    return parseDependenciesFromSbom(JSON.parse(text));
  };

  const handleFileUpload = async (event) => {
    const input = event.target;
    const file = input.files?.[0];
    input.value = "";

    if (!file || !activeSbom) {
      return;
    }

    try {
      await readSbomFile(file);
    } catch {
      window.alert(
        "SBOM JSONの読み込みに失敗しました。CycloneDX JSONまたはSPDX JSONを確認してください。",
      );
      return;
    }

    setPendingUpload({ file, serviceName: activeSbom.title });
  };

  const handleImageUpload = (event) => {
    const input = event.target;
    const file = input.files?.[0];

    if (!file || !activeSbom) {
      return;
    }

    if (!file.type.startsWith("image/")) {
      window.alert("画像ファイルを選択してください。");
      input.value = "";
      return;
    }

    const reader = new FileReader();

    reader.onload = () => updateActiveSbom({ imageUrl: String(reader.result || "") });
    reader.onerror = () => window.alert("画像の読み込みに失敗しました。");
    reader.readAsDataURL(file);
    input.value = "";
  };

  const handleCreateFileUpload = async (event) => {
    const input = event.target;
    const file = input.files?.[0];
    input.value = "";

    if (!file) {
      return;
    }

    try {
      await readSbomFile(file);
    } catch {
      window.alert(
        "SBOM JSONの読み込みに失敗しました。CycloneDX JSONまたはSPDX JSONを確認してください。",
      );
      return;
    }

    setPendingUpload({ file });
  };

  if (!activeSbom && !isCreatingSbom) {
    return null;
  }

  return (
    <Box
      sx={{
        bgcolor: slate[100],
        color: slate[950],
        minHeight: "100vh",
        overflowX: "hidden",
        p: { sm: 3, xs: 1.5 },
      }}
    >
      <Box sx={{ maxWidth: 1600, minWidth: 0, mx: "auto", width: "100%" }}>
        <Stack
          direction="row"
          alignItems="flex-end"
          sx={{
            borderBottom: `1px solid ${slate[200]}`,
            gap: 1,
            minWidth: 0,
            overflowX: "auto",
            px: 0.5,
            width: "100%",
          }}
        >
          {sboms.map((sbom) => (
            <TabButton
              active={sbom.id === activeId}
              key={sbom.id}
              onClick={() => {
                setActiveId(sbom.id);
                resetUiState();
              }}
              sbom={sbom}
            />
          ))}
          <Box
            component="button"
            onClick={addSbom}
            sx={{
              "&:hover": { bgcolor: "white", borderColor: slate[400], color: slate[900] },
              alignItems: "center",
              bgcolor: isCreatingSbom ? "white" : slate[50],
              border: "1px solid",
              borderColor: isCreatingSbom ? slate[200] : slate[300],
              borderStyle: isCreatingSbom ? "solid" : "dashed",
              borderTopLeftRadius: 16,
              borderTopRightRadius: 16,
              boxShadow: isCreatingSbom ? "0 1px 2px rgba(15, 23, 42, 0.05)" : "none",
              color: isCreatingSbom ? slate[950] : slate[500],
              cursor: "pointer",
              display: "flex",
              font: "inherit",
              fontSize: 14,
              fontWeight: 600,
              gap: 1,
              ml: 0.5,
              px: 2.5,
              py: 1.5,
              transition: "background-color 160ms ease, color 160ms ease, border-color 160ms ease",
              whiteSpace: "nowrap",
            }}
            type="button"
          >
            <AddIcon sx={{ fontSize: 18 }} />
            新規登録
          </Box>
        </Stack>

        {isCreatingSbom ? (
          <NewSbomRegistrationPanel
            inputRef={createFileInputRef}
            onCancel={cancelCreateSbom}
            onFileChange={handleCreateFileUpload}
            showCancel={!isEmpty}
          />
        ) : (
          <Box
            sx={{
              bgcolor: "white",
              borderBottomLeftRadius: 24,
              borderBottomRightRadius: 24,
              borderTopRightRadius: 24,
              boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
              display: "grid",
              gap: 3,
              gridTemplateColumns: {
                lg: "minmax(280px, 0.7fr) minmax(0, 1.9fr)",
                xl: "minmax(320px, 0.75fr) minmax(0, 2.35fr)",
                xs: "1fr",
              },
              minWidth: 0,
              p: { sm: 2.5, xs: 1.5 },
              width: "100%",
            }}
          >
            <Box sx={{ display: "flex", flexDirection: "column", gap: 1, minWidth: 0 }}>
              <Card
                sx={{
                  border: `1px solid ${slate[200]}`,
                  borderRadius: 6,
                  boxShadow: "none",
                  minWidth: 0,
                  overflow: "hidden",
                }}
              >
                <SbomImage
                  editing={detailsEditing}
                  imageUrl={activeSbom.imageUrl}
                  onImageUpload={handleImageUpload}
                  onRemoveImage={() => updateActiveSbom({ imageUrl: "" })}
                  title={activeSbom.title}
                />
                <AccordionHeader
                  action={
                    <HeaderActionButton
                      active={detailsEditing}
                      icon={detailsEditing ? CheckIcon : EditIcon}
                      onClick={() => {
                        setDetailsOpen(true);
                        setDetailsEditing((editing) => !editing);
                      }}
                    >
                      {detailsEditing ? "完了" : "編集"}
                    </HeaderActionButton>
                  }
                  icon={InfoOutlinedIcon}
                  onToggle={() => setDetailsOpen((open) => !open)}
                  open={detailsOpen}
                  title="詳細情報"
                />
                <CardContent
                  sx={{
                    display: { md: "block", xs: detailsOpen ? "block" : "none" },
                    minWidth: 0,
                    pb: 1.5,
                    pt: 0,
                    px: 2,
                  }}
                >
                  <DetailsForm
                    editing={detailsEditing}
                    onUpdate={updateActiveSbom}
                    open={detailsOpen}
                    sbom={activeSbom}
                  />
                </CardContent>
              </Card>

              <Card
                sx={{
                  border: `1px solid ${slate[200]}`,
                  borderRadius: 6,
                  boxShadow: "none",
                  minWidth: 0,
                }}
              >
                <AccordionHeader
                  action={
                    <Stack direction="row" alignItems="center" sx={{ gap: 1, height: 32 }}>
                      <CountBadge>{activeSbom.deployments.length}件</CountBadge>
                      {deploymentsEditing && (
                        <HeaderActionButton
                          icon={AddIcon}
                          onClick={addDeployment}
                          sx={{
                            display: {
                              md: "inline-flex",
                              xs: deploymentsOpen ? "inline-flex" : "none",
                            },
                          }}
                        >
                          追加
                        </HeaderActionButton>
                      )}
                      <HeaderActionButton
                        active={deploymentsEditing}
                        icon={deploymentsEditing ? CheckIcon : EditIcon}
                        onClick={() => {
                          setDeploymentsOpen(true);
                          setDeploymentsEditing((editing) => !editing);
                        }}
                      >
                        {deploymentsEditing ? "完了" : "編集"}
                      </HeaderActionButton>
                    </Stack>
                  }
                  icon={StorageRoundedIcon}
                  onToggle={() => setDeploymentsOpen((open) => !open)}
                  open={deploymentsOpen}
                  title="デプロイ先"
                />
                <DeploymentList
                  deployments={activeSbom.deployments}
                  editing={deploymentsEditing}
                  onRemove={removeDeployment}
                  onUpdate={updateDeployment}
                  open={deploymentsOpen}
                />
              </Card>

              <DangerZone
                onDelete={removeActiveSbom}
                onToggle={() => setDangerOpen((open) => !open)}
                open={dangerOpen}
                sbomTitle={activeSbom.title}
              />
            </Box>

            <Card
              sx={{
                border: `1px solid ${slate[200]}`,
                borderRadius: 6,
                boxShadow: "none",
                minWidth: 0,
              }}
            >
              <CardContent sx={{ minWidth: 0, p: 3 }}>
                <Box
                  sx={{
                    border: `1px solid ${slate[200]}`,
                    borderRadius: 4,
                    minWidth: 0,
                    overflow: "hidden",
                    width: "100%",
                  }}
                >
                  <Box
                    sx={{
                      alignItems: { md: "center", xs: "stretch" },
                      bgcolor: "rgba(248, 250, 252, 0.7)",
                      borderBottom: `1px solid ${slate[200]}`,
                      display: "flex",
                      flexWrap: "wrap",
                      gap: 1.5,
                      px: 1.5,
                      py: 1.25,
                    }}
                  >
                    <Box
                      sx={{
                        bgcolor: "white",
                        border: `1px solid ${slate[200]}`,
                        borderRadius: 3,
                        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
                        flex: { md: "0 1 520px", xs: "1 1 100%" },
                        height: 36,
                        minWidth: { md: 280, xs: 0 },
                        position: "relative",
                      }}
                    >
                      <SearchIcon
                        sx={{
                          color: slate[400],
                          fontSize: 17,
                          left: 12,
                          pointerEvents: "none",
                          position: "absolute",
                          top: "50%",
                          transform: "translateY(-50%)",
                        }}
                      />
                      <Box
                        component="input"
                        onChange={(event) => {
                          setCurrentPage(1);
                          setQuery(event.target.value);
                        }}
                        placeholder="名前・バージョン・ライセンス検索"
                        sx={{
                          "&::placeholder": { color: slate[400], opacity: 1 },
                          bgcolor: "transparent",
                          border: 0,
                          boxSizing: "border-box",
                          color: slate[700],
                          display: "block",
                          font: "inherit",
                          fontSize: 13,
                          height: "100%",
                          lineHeight: "18px",
                          outline: "none",
                          pl: "34px",
                          pr: 1.25,
                          py: 0,
                          width: "100%",
                        }}
                        value={query}
                      />
                    </Box>
                    <Typography
                      sx={{
                        alignSelf: "center",
                        color: slate[500],
                        flex: { md: "0 0 auto", xs: "1 1 auto" },
                        fontSize: 13,
                        lineHeight: "18px",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {filteredDependencies.length === 0
                        ? "依存関係がありません"
                        : `${filteredDependencies.length}件中 ${pageStartIndex + 1}-${pageEndIndex}件`}
                    </Typography>
                    <Box sx={{ flex: { md: "1 1 auto", xs: "0 0 auto" } }} />
                    <Box
                      accept=".json,application/json"
                      component="input"
                      onChange={handleFileUpload}
                      ref={fileInputRef}
                      sx={{ display: "none" }}
                      type="file"
                    />
                    <AppButton
                      onClick={() => fileInputRef.current?.click()}
                      size="small"
                      startIcon={<UploadFileIcon />}
                      sx={{ alignSelf: { md: "auto", xs: "center" }, bgcolor: "white" }}
                      variant="outlined"
                    >
                      SBOM更新
                    </AppButton>
                  </Box>

                  <Box sx={{ minWidth: 0, overflowX: "auto", width: "100%" }}>
                    <Box sx={{ minWidth: { lg: 0, xs: 640 }, width: "100%" }}>
                      <Box
                        sx={{
                          bgcolor: slate[50],
                          color: slate[500],
                          display: "grid",
                          fontSize: 12,
                          fontWeight: 700,
                          gridTemplateColumns: "48px 1.4fr 0.7fr 0.65fr 0.8fr",
                          letterSpacing: 0,
                          px: 2,
                          py: 1.5,
                          textTransform: "uppercase",
                        }}
                      >
                        <Box>SSVC</Box>
                        <Box>パッケージ</Box>
                        <Box>バージョン</Box>
                        <Box>種別</Box>
                        <Box>ライセンス</Box>
                      </Box>
                      <DependencyTable
                        dependencies={paginatedDependencies}
                        onPackageClick={onPackageClick}
                        pageStartIndex={pageStartIndex}
                      />
                    </Box>
                  </Box>

                  {filteredDependencies.length > 0 && (
                    <Box
                      sx={{
                        alignItems: { md: "center" },
                        bgcolor: "white",
                        borderTop: `1px solid ${slate[200]}`,
                        display: "flex",
                        flexDirection: { md: "row", xs: "column" },
                        gap: 1.5,
                        justifyContent: "space-between",
                        px: 2,
                        py: 1.25,
                      }}
                    >
                      <Box
                        sx={{
                          alignItems: "center",
                          color: slate[500],
                          display: "flex",
                          flexShrink: 0,
                          gap: 1.25,
                          minHeight: 34,
                        }}
                      >
                        <Typography
                          sx={{
                            color: slate[500],
                            fontSize: 13,
                            lineHeight: "18px",
                            whiteSpace: "nowrap",
                          }}
                        >
                          表示件数
                        </Typography>
                        <Select
                          onChange={(event) => {
                            setCurrentPage(1);
                            setPageSize(Number(event.target.value));
                          }}
                          size="small"
                          sx={compactSelectSx}
                          value={pageSize}
                        >
                          <MenuItem value={10}>10件</MenuItem>
                          <MenuItem value={20}>20件</MenuItem>
                          <MenuItem value={50}>50件</MenuItem>
                        </Select>
                      </Box>
                      <Box
                        sx={{
                          alignItems: "center",
                          display: "flex",
                          flexWrap: "wrap",
                          gap: 1.25,
                          justifyContent: { md: "flex-end", xs: "space-between" },
                          minWidth: 0,
                        }}
                      >
                        <Typography
                          sx={{
                            color: slate[600],
                            flexShrink: 0,
                            fontSize: 13,
                            fontWeight: 600,
                            lineHeight: "18px",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {safeCurrentPage} / {totalPages}ページ
                        </Typography>
                        <Stack direction="row" alignItems="center" sx={{ gap: 0.75 }}>
                          <AppButton
                            disabled={safeCurrentPage <= 1}
                            onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                            size="small"
                            startIcon={<ChevronLeftIcon />}
                            variant="outlined"
                          >
                            前へ
                          </AppButton>
                          <AppButton
                            disabled={safeCurrentPage >= totalPages}
                            onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                            size="small"
                            endIcon={<ChevronRightIcon />}
                            variant="outlined"
                          >
                            次へ
                          </AppButton>
                        </Stack>
                      </Box>
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Box>
        )}
      </Box>
      <SBOMUpdateDialog
        open={!!pendingUpload}
        onClose={() => setPendingUpload(null)}
        pteamId={pteamId}
        initialFile={pendingUpload?.file ?? null}
        serviceName={pendingUpload?.serviceName}
        existingServiceNames={
          pendingUpload && !pendingUpload.serviceName
            ? sboms.map((sbom) => sbom.title)
            : undefined
        }
        showWarning={!!pendingUpload?.serviceName}
        onUploaded={() => setPendingUpload(null)}
      />
    </Box>
  );
}

export default SBOMManagement;
