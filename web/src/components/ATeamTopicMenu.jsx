import { Button, Box } from "@mui/material";
import React, { useState } from "react";

import styles from "../cssModule/button.module.css";

import { ATeamTopicCreateModal } from "./ATeamTopicCreateModal";

export function ATeamTopicMenu() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <Box display="flex" justifyContent="flex-end" mb={2}>
        <Button
          className={styles.prominent_btn}
          onClick={() => {
            setModalOpen(true);
          }}
          sx={{ width: "100px" }}
        >
          New Topic
        </Button>
        <ATeamTopicCreateModal open={modalOpen} onSetOpen={setModalOpen} />
      </Box>
    </>
  );
}
