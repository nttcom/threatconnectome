import { Box, Tooltip } from "@mui/material";
import { orange } from "@mui/material/colors";
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

export default function ActionTypeIcon(props) {
  const { disabled, actionType } = props;

  return (
    <Box sx={{ mr: 0.5 }}>
      {disabled ? (
        <>
          <IconContext.Provider value={{ color: "disabled", size: "25px" }}>
            {actionTypeChipColors[actionType]}
          </IconContext.Provider>
        </>
      ) : (
        <>
          <Tooltip arrow placement="bottom" title="recommended">
            <Box>
              <IconContext.Provider value={{ color: orange[900], size: "25px" }}>
                {actionTypeChipColors[actionType]}
              </IconContext.Provider>
            </Box>
          </Tooltip>
        </>
      )}
    </Box>
  );
}

ActionTypeIcon.propTypes = {
  disabled: PropTypes.bool.isRequired,
  sx: PropTypes.object,
  actionType: PropTypes.string.isRequired,
};
