import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import PropTypes from "prop-types";
import React from "react";

const noImageAvailableUrl = "images/720x480.png";

export function DeleteServiceImageAlertDialog(props) {
  const {
    isDeleteDialogOpen,
    setIsDeleteDialogOpen,
    setImageFileData,
    setImageDeleteFlag,
    setImagePreview,
  } = props;

  const handleCloseCancel = () => {
    setIsDeleteDialogOpen(false);
  };

  const handleDelete = () => {
    setIsDeleteDialogOpen(false);
    setImageFileData(null);
    setImageDeleteFlag(true);
    setImagePreview(noImageAvailableUrl);
  };

  return (
    <>
      <Dialog open={isDeleteDialogOpen} onClose={handleCloseCancel}>
        <DialogTitle>Warning</DialogTitle>
        <DialogContent>
          <DialogContentText>Are you sure you want to delete the image?</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCancel}>Cancel</Button>
          <Button variant="contained" onClick={handleDelete}>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

DeleteServiceImageAlertDialog.propTypes = {
  isDeleteDialogOpen: PropTypes.bool,
  setIsDeleteDialogOpen: PropTypes.func,
  setImageFileData: PropTypes.func,
  setImageDeleteFlag: PropTypes.func,
  setImagePreview: PropTypes.func,
};
