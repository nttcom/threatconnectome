import { AddBox as AddBoxIcon } from "@mui/icons-material";
import { Dialog, DialogContent, IconButton } from "@mui/material";
import { blue } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useState } from "react";

import { ActionGenerator } from "./ActionGenerator";

export function ActionGeneratorModal(props) {
  const { actionTagOptions, actions, setActions } = props;
  const [generatorOpen, setGeneratorOpen] = useState(false);
  return (
    <>
      <IconButton onClick={() => setGeneratorOpen(true)} sx={{ color: blue[700] }}>
        <AddBoxIcon />
      </IconButton>
      <Dialog open={generatorOpen} onClose={() => setGeneratorOpen(false)}>
        <DialogContent>
          <ActionGenerator
            text="Add action"
            tagIds={actionTagOptions}
            onGenerate={(ret) => {
              setActions([...actions, ret]);
              setGeneratorOpen(false);
            }}
            onCancel={() => setGeneratorOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

ActionGeneratorModal.propTypes = {
  actionTagOptions: PropTypes.array.isRequired,
  actions: PropTypes.array.isRequired,
  setActions: PropTypes.func.isRequired,
};
