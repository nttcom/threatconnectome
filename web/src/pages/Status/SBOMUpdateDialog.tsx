import {
  Close as CloseIcon,
  LockOutlined as LockIcon,
  UploadFile as UploadFileIcon,
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
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";

type Props = {
  open: boolean;
  onClose: () => void;
};

export function SBOMUpdateDialog({ open, onClose }: Props) {
  const theme = useTheme();
  const isMdDown = useMediaQuery(theme.breakpoints.down("md"));

  return (
    <Dialog fullWidth open={open} onClose={onClose}>
      <DialogTitle>
        <Box sx={{ alignItems: "center", display: "flex", flexDirection: "row" }}>
          <Typography variant="h6" flexGrow={1}>
            SBOM を更新
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
          <TextField
            label="サービス名"
            size="small"
            value="sample-service"
            disabled
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <LockIcon fontSize="small" />
                  </InputAdornment>
                ),
              },
            }}
          />
          <Box
            sx={{
              alignItems: "center",
              justifyContent: "center",
              display: "flex",
              flexDirection: "column",
              width: "100%",
              minHeight: "300px",
              border: "4px dotted #888",
            }}
          >
            <UploadFileIcon sx={{ fontSize: 50, mb: 3 }} />
            <Typography variant="body2">
              {isMdDown ? "タップして選択" : "ドロップまたはクリックして選択"}
            </Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button disabled>アップロード</Button>
      </DialogActions>
    </Dialog>
  );
}
