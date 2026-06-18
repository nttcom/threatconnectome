import { useRef, useState } from "react";

import { validateSbomFileSelection } from "./sbomFileValidation";

type UseSbomFileDropOptions = {
  onFile: (file: File) => void;
  onError: (errorKey: string) => void;
};

export function useSbomFileDrop({ onFile, onError }: UseSbomFileDropOptions) {
  const dragCounterRef = useRef(0);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragEnter = (event: React.DragEvent) => {
    event.preventDefault();
    dragCounterRef.current++;
    setIsDragOver(true);
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDragLeave = () => {
    if (--dragCounterRef.current === 0) setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    dragCounterRef.current = 0;
    setIsDragOver(false);
    const result = validateSbomFileSelection(event.dataTransfer.files);
    if (result.error) onError(result.error);
    else if (result.file) onFile(result.file);
  };

  return { isDragOver, handleDragEnter, handleDragOver, handleDragLeave, handleDrop };
}
