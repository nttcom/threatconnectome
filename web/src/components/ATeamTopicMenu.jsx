import { Button, Box } from "@mui/material";
import PropTypes from "prop-types";
import React, { useState } from "react";

import styles from "../cssModule/button.module.css";

import { ATeamTopicCreateModal } from "./ATeamTopicCreateModal";

export function ATeamTopicMenu(props) {
  const { ateamId } = props;
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
        <ATeamTopicCreateModal ateamId={ateamId} open={modalOpen} onSetOpen={setModalOpen} />
      </Box>
    </>
  );
}
ATeamTopicMenu.propTypes = {
  ateamId: PropTypes.string.isRequired,
};
