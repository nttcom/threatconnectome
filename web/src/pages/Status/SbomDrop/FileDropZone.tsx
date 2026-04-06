import { UploadFile as UploadFileIcon } from "@mui/icons-material";
import { Box, Typography } from "@mui/material";
import { useRef } from "react";
import { useTranslation } from "react-i18next";

type FileDropZoneProps = {
  onFileSelected: (file: File) => void;
  selectedFile?: File | null;
  showFileName?: boolean;
};

export function FileDropZone({
  onFileSelected,
  selectedFile = null,
  showFileName = true,
}: FileDropZoneProps) {
  const { t } = useTranslation("status", { keyPrefix: "FileDropZone" });
  const dropRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndSetFile = (files: FileList | null) => {
    if (!files || !files.length) return;

    if (files.length > 1) {
      alert(t("alertOnlyOneFile"));
      return;
    }
    if (!files[0].name.endsWith(".json")) {
      alert(t("alertOnlyJson"));
      return;
    }
    onFileSelected(files[0]);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    validateAndSetFile(event.dataTransfer.files);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    validateAndSetFile(event.target.files);
    event.target.value = "";
  };

  return (
    <Box
      ref={dropRef}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleClick}
      sx={{
        alignItems: "center",
        justifyContent: "center",
        display: "flex",
        flexDirection: "column",
        width: "100%",
        minHeight: "300px",
        border: "4px dotted #888",
        cursor: "pointer",
      }}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
      <UploadFileIcon sx={{ fontSize: 50, mb: 3 }} />
      {showFileName && selectedFile ? (
        <Typography variant="body2" sx={{ fontWeight: "bold" }}>
          {selectedFile.name}
        </Typography>
      ) : (
        t("dropOrClickToSelect")
      )}
    </Box>
  );
}
