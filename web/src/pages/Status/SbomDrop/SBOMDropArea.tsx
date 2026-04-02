import { useState } from "react";

import { FileDropZone } from "./FileDropZone";
import { SBOMUpdateDialog } from "./SBOMUpdateDialog";

interface SBOMDropAreaProps {
  pteamId: string;
  onUploaded: () => void;
  existingServiceNames?: string[];
}

export function SBOMDropArea({ pteamId, onUploaded, existingServiceNames }: SBOMDropAreaProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleFileSelected = (file: File) => {
    setSelectedFile(file);
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setSelectedFile(null);
    setDialogOpen(false);
  };

  if (!pteamId) return <></>;

  return (
    <>
      <FileDropZone
        onFileSelected={handleFileSelected}
        selectedFile={null}
        allowClick={true}
        showFileName={false}
      />
      <SBOMUpdateDialog
        open={dialogOpen}
        onClose={handleDialogClose}
        pteamId={pteamId}
        initialFile={selectedFile}
        onUploaded={onUploaded}
        existingServiceNames={existingServiceNames}
      />
    </>
  );
}
