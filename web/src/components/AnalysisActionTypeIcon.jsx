import { Box } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";
import { IconContext } from "react-icons";
import { FaSkullCrossbones, FaVirusSlash } from "react-icons/fa";
import { MdDoNotTouch, MdPolicy } from "react-icons/md";
import { TbArrowFork, TbWall } from "react-icons/tb";

export const actionTypeChipColors = {
  elimination: <FaVirusSlash />,
  mitigation: <TbWall />,
  detection: <MdPolicy />,
  transfer: <TbArrowFork />,
  acceptance: <FaSkullCrossbones />,
  rejection: <MdDoNotTouch />,
};

export default function AnalysisActionTypeIcon(props) {
  const { actionType } = props;

  return (
    <Box sx={{ mr: 0.5 }}>
      <IconContext.Provider value={{ color: grey[700], size: "20px" }}>
        {actionTypeChipColors[actionType]}
      </IconContext.Provider>
    </Box>
  );
}

AnalysisActionTypeIcon.propTypes = {
  sx: PropTypes.object,
  actionType: PropTypes.string.isRequired,
};
