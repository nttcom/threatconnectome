import { Button, Box } from "@mui/material";
import React, { useState } from "react";

import { commonButtonStyle } from "../utils/const";

import { ATeamTopicCreateModal } from "./ATeamTopicCreateModal";

export function ATeamTopicMenu() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <Box display="flex" justifyContent="flex-end" mb={2}>
        <Button
          onClick={() => {
            setModalOpen(true);
          }}
          sx={{ ...commonButtonStyle, width: "100px" }}
        >
          New Topic
        </Button>
        <ATeamTopicCreateModal open={modalOpen} onSetOpen={setModalOpen} />
      </Box>
    </>
  );
}
