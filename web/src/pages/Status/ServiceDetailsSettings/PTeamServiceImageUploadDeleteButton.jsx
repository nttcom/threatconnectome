import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DeleteIcon from "@mui/icons-material/Delete";
import { ButtonGroup } from "@mui/material";
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import { styled } from "@mui/material/styles";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { serviceImageMaxSize } from "../../../utils/const";
import { normalizeServiceImageToPng } from "../../../utils/serviceImageUtils";

export function PTeamServiceImageUploadDeleteButton(props) {
  const {
    setImageFileData,
    setImageDeleteFlag,
    setImagePreview,
    setIsImageChanged,
    originalImage,
  } = props;
  const { t } = useTranslation("status", { keyPrefix: "PTeamServiceImageUploadDeleteButton" });

  const [anchorEl, setAnchorEl] = useState(null);

  const { enqueueSnackbar } = useSnackbar();
  const serviceDetailsSettingNoImageUrl = "images/720x480.png";

  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const handleUploadImage = async (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    if (selectedFile.size >= serviceImageMaxSize) {
      enqueueSnackbar(t("fileSizeExceeds"), { variant: "error" });
      return;
    }

    try {
      const normalizedImage = await normalizeServiceImageToPng(selectedFile);

      if (normalizedImage.file.size >= serviceImageMaxSize) {
        enqueueSnackbar(t("normalizedFileSizeExceeds"), { variant: "error" });
        return;
      }

      setImageFileData(normalizedImage.file);
      setImageDeleteFlag(false);
      setImagePreview(normalizedImage.previewDataUrl);
      setIsImageChanged(originalImage !== normalizedImage.previewDataUrl);
    } catch {
      enqueueSnackbar(t("imageProcessingFailed"), { variant: "error" });
    }
  };

  const handleDelete = () => {
    setImageFileData(null);
    setImageDeleteFlag(true);
    setImagePreview(serviceDetailsSettingNoImageUrl);
    if (originalImage === "images/720x480.png") {
      setIsImageChanged(false);
    } else {
      setIsImageChanged(true);
    }
  };

  const VisuallyHiddenInput = styled("input")({
    clip: "rect(0 0 0 0)",
    clipPath: "inset(50%)",
    height: 1,
    overflow: "hidden",
    position: "absolute",
    bottom: 0,
    left: 0,
    whiteSpace: "nowrap",
    width: 1,
  });

  return (
    <>
      <ButtonGroup variant="contained" aria-label="Button group with a nested menu">
        <Button component="label" tabIndex={-1} startIcon={<CloudUploadIcon />}>
          {t("uploadImage")}
          <VisuallyHiddenInput
            type="file"
            accept=".png"
            onChange={(event) => {
              handleUploadImage(event);
            }}
          />
        </Button>
        <Button size="small" onClick={handleClick}>
          <ArrowDropDownIcon />
        </Button>
      </ButtonGroup>
      <Menu anchorEl={anchorEl} open={open} onClose={handleClose}>
        <MenuItem
          onClick={() => {
            handleClose();
            handleDelete();
          }}
        >
          <DeleteIcon sx={{ mr: 1 }} />
          {t("deleteImage")}
        </MenuItem>
      </Menu>
    </>
  );
}

PTeamServiceImageUploadDeleteButton.propTypes = {
  setImageFileData: PropTypes.func.isRequired,
  setImageDeleteFlag: PropTypes.func.isRequired,
  setImagePreview: PropTypes.func.isRequired,
  setIsImageChanged: PropTypes.func.isRequired,
  originalImage: PropTypes.string.isRequired,
};
