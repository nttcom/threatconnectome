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

import {
  serviceImageHeightSize,
  serviceImageWidthSize,
  serviceImageMaxSize,
} from "../../../utils/const";

export function PTeamServiceImageUploadDeleteButton(props) {
  const { setImageFileData, setImageDeleteFlag, setImagePreview } = props;

  const [anchorEl, setAnchorEl] = useState(null);

  const { enqueueSnackbar } = useSnackbar();
  const serviceDetailsSetttingNoImageUrl = "images/720x480.png";

  const open = Boolean(anchorEl);
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };
  const handleUploadImage = (event) => {
    if (event.target.files[0].size >= serviceImageMaxSize) {
      enqueueSnackbar("Filesize exceeds max(512KiB)", { variant: "error" });
      return;
    }

    const reader = new FileReader();
    const image = new Image();
    reader.onload = (e) => {
      image.src = e.target?.result;
      image.onload = () => {
        if (
          image.naturalWidth === serviceImageWidthSize &&
          image.naturalHeight === serviceImageHeightSize
        ) {
          setImageFileData(event.target.files[0]);
          setImageDeleteFlag(false);
          setImagePreview(e.target?.result);
        } else {
          enqueueSnackbar(
            `Dimensions must be ${serviceImageWidthSize}px ${serviceImageHeightSize} px`,
            {
              variant: "error",
            },
          );
          return;
        }
      };
    };
    reader.readAsDataURL(event.target.files[0]);
  };

  const handleDelete = () => {
    setImageFileData(null);
    setImageDeleteFlag(true);
    setImagePreview(serviceDetailsSetttingNoImageUrl);
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
      <Menu anchorEl={anchorEl} open={open} onClose={handleClose} onClick={handleDelete}>
        <MenuItem
          onClick={() => {
            handleClose();
          }}
        >
          <DeleteIcon sx={{ mr: 1 }} />
          Delete image
        </MenuItem>
      </Menu>
    </>
  );
}

PTeamServiceImageUploadDeleteButton.propTypes = {
  setImageFileData: PropTypes.func.isRequired,
  setImageDeleteFlag: PropTypes.func.isRequired,
  setImagePreview: PropTypes.func.isRequired,
};
