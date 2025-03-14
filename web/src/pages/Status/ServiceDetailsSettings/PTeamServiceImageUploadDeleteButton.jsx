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
import React, { useState } from "react";

import { imageHeightSize, imageWidthSize, imageMaxSize } from "../../../utils/const";

import { DeleteServiceImageAlertDialog } from "./DeleteServiceImageAlertDialog";

export function PTeamServiceImageUploadDeleteButton(props) {
  const { setImageFileData, setImageDeleteFlag, setImagePreview } = props;

  const [anchorEl, setAnchorEl] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const handleUploadImage = (event) => {
    if (event.target.files[0].size >= imageMaxSize) {
      enqueueSnackbar("Filesize exceeds max(512KiB)", { variant: "error" });
      return;
    }

    const reader = new FileReader();
    const image = new Image();
    reader.onload = (e) => {
      image.src = e.target?.result;
      image.onload = () => {
        if (image.naturalWidth === imageWidthSize && image.naturalHeight === imageHeightSize) {
          setImageFileData(event.target.files[0]);
          setImageDeleteFlag(false);
          setImagePreview(e.target?.result);
        } else {
          enqueueSnackbar(`Dimensions must be ${imageWidthSize}px ${imageHeightSize} px`, {
            variant: "error",
          });
          return;
        }
      };
    };
    reader.readAsDataURL(event.target.files[0]);
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
          Upload image
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
            setIsDeleteDialogOpen(true);
          }}
        >
          <DeleteIcon sx={{ mr: 1 }} />
          Delete image
        </MenuItem>
      </Menu>
      <DeleteServiceImageAlertDialog
        isDeleteDialogOpen={isDeleteDialogOpen}
        setIsDeleteDialogOpen={setIsDeleteDialogOpen}
        setImageFileData={setImageFileData}
        setImageDeleteFlag={setImageDeleteFlag}
        setImagePreview={setImagePreview}
      />
    </>
  );
}

PTeamServiceImageUploadDeleteButton.propTypes = {
  setImageFileData: PropTypes.func.isRequired,
  setImageDeleteFlag: PropTypes.func.isRequired,
  setImagePreview: PropTypes.func.isRequired,
};
