import { AddBox as AddBoxIcon } from "@mui/icons-material";
import { Dialog, DialogContent, IconButton } from "@mui/material";
import { blue } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { TopicTagSelector } from "./TopicTagSelector";

export function TopicTagSelectorModal(props) {
  const { tagIds, setTagIds, setActionTagOptions, createActionTagOptions } = props;
  const [tagOpen, setTagOpen] = useState(false);

  return (
    <>
      <IconButton onClick={() => setTagOpen(true)} sx={{ color: blue[700] }}>
        <AddBoxIcon />
      </IconButton>
      <Dialog open={tagOpen} onClose={() => setTagOpen(false)}>
        <DialogContent>
          <TopicTagSelector
            currentSelectedIds={tagIds}
            onCancel={() => setTagOpen(false)}
            onApply={(ary) => {
              setTagIds(ary);
              setActionTagOptions(createActionTagOptions(ary));
              setTagOpen(false);
            }}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

TopicTagSelectorModal.propTypes = {
  tagIds: PropTypes.array.isRequired,
  setTagIds: PropTypes.func.isRequired,
  setActionTagOptions: PropTypes.func.isRequired,
  createActionTagOptions: PropTypes.func.isRequired,
};
