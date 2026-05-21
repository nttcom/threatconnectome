import { serviceImageHeightSize, serviceImageWidthSize } from "./const";

export type CropRect = {
  sx: number;
  sy: number;
  sWidth: number;
  sHeight: number;
};

export function calculateCenteredCropRect(
  sourceWidth: number,
  sourceHeight: number,
  targetWidth: number,
  targetHeight: number,
): CropRect {
  const sourceAspectRatio = sourceWidth / sourceHeight;
  const targetAspectRatio = targetWidth / targetHeight;

  if (sourceAspectRatio > targetAspectRatio) {
    const cropWidth = sourceHeight * targetAspectRatio;
    return {
      sx: (sourceWidth - cropWidth) / 2,
      sy: 0,
      sWidth: cropWidth,
      sHeight: sourceHeight,
    };
  }

  const cropHeight = sourceWidth / targetAspectRatio;
  return {
    sx: 0,
    sy: (sourceHeight - cropHeight) / 2,
    sWidth: sourceWidth,
    sHeight: cropHeight,
  };
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result;
      if (typeof result !== "string") {
        reject(new Error("Failed to read selected file"));
        return;
      }
      resolve(result);
    };
    reader.onerror = () => {
      reject(new Error("Failed to read selected file"));
    };
    reader.readAsDataURL(file);
  });
}

function loadImage(dataUrl: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("Failed to decode selected image"));
    image.src = dataUrl;
  });
}

function canvasToBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error("Failed to convert image"));
        return;
      }
      resolve(blob);
    }, "image/png");
  });
}

function toPngFileName(fileName: string): string {
  const normalizedName = fileName.replace(/\.[^/.]+$/, "");
  return `${normalizedName}.png`;
}

export type NormalizedServiceImage = {
  file: File;
  previewDataUrl: string;
};

export async function normalizeServiceImageToPng(file: File): Promise<NormalizedServiceImage> {
  const sourceDataUrl = await readFileAsDataUrl(file);
  const sourceImage = await loadImage(sourceDataUrl);
  const cropRect = calculateCenteredCropRect(
    sourceImage.naturalWidth,
    sourceImage.naturalHeight,
    serviceImageWidthSize,
    serviceImageHeightSize,
  );

  const canvas = document.createElement("canvas");
  canvas.width = serviceImageWidthSize;
  canvas.height = serviceImageHeightSize;

  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Canvas context is not available");
  }

  context.drawImage(
    sourceImage,
    cropRect.sx,
    cropRect.sy,
    cropRect.sWidth,
    cropRect.sHeight,
    0,
    0,
    serviceImageWidthSize,
    serviceImageHeightSize,
  );

  const outputBlob = await canvasToBlob(canvas);
  const outputFile = new File([outputBlob], toPngFileName(file.name), { type: "image/png" });

  return {
    file: outputFile,
    previewDataUrl: canvas.toDataURL("image/png"),
  };
}
