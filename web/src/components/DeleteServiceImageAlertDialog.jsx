import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import PropTypes from "prop-types";
import React from "react";

export function DeleteServiceImageAlertDialog(props) {
  const { isDeleteDialogOpen, setIsDeleteDialogOpen, setImageFileData, setImageDeleteFlag } = props;

  const handleClose = () => {
    setIsDeleteDialogOpen(false);
    setImageFileData(null);
    setImageDeleteFlag(true);
  };

  return (
    <>
      <Dialog open={isDeleteDialogOpen} onClose={handleClose}>
        <DialogTitle>Warning</DialogTitle>
        <DialogContent>
          <DialogContentText>Are you sure you want to delete the image?</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button variant="contained" onClick={handleClose}>
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
};
