import { UploadFile as UploadFileIcon } from "@mui/icons-material";
import { Box, Typography } from "@mui/material";
import { useRef } from "react";
import { useTranslation } from "react-i18next";

import { uiPalette, uiTransitions } from "../../../styles/designTokens";

import { validateSbomFileSelection } from "./sbomFileValidation";
import { useSbomFileDrop } from "./useSbomFileDrop";

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

  const { isDragOver, handleDragEnter, handleDragOver, handleDragLeave, handleDrop } =
    useSbomFileDrop({
      onFile: onFileSelected,
      onError: (key) => alert(t(key)),
    });

  const handleFileInputChange = (files: FileList | null) => {
    const result = validateSbomFileSelection(files);
    if (result.error) {
      alert(t(result.error));
      return;
    }
    if (result.file) {
      onFileSelected(result.file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFileInputChange(event.target.files);
    event.target.value = "";
  };

  return (
    <Box
      ref={dropRef}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
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
        border: isDragOver
          ? `4px dashed ${uiPalette.slate[600]}`
          : `4px dotted ${uiPalette.slate[400]}`,
        bgcolor: isDragOver ? uiPalette.slate[50] : "transparent",
        cursor: "pointer",
        transition: uiTransitions.borderOnly,
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
