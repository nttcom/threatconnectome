// ResponsiveDrawer.jsx

import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { Box, Drawer, IconButton, Tooltip, Typography } from "@mui/material";
import PropTypes from "prop-types";

export function ResponsiveDrawer({ open, onClose, title, children }) {
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      {/* ▼ 変更: 元のUIに合わせてBoxの構造を変更 */}
      <Box>
        <Tooltip arrow title="Close">
          <IconButton size="large" onClick={onClose}>
            <KeyboardDoubleArrowRightIcon fontSize="inherit" />
          </IconButton>
        </Tooltip>
      </Box>
      <Box sx={{ width: { xs: "100vw", md: 800 }, px: 3, boxSizing: "border-box" }}>
        <Typography variant="h4" sx={{ pb: 1, fontWeight: "bold" }}>
          {title}
        </Typography>
        {children}
      </Box>
    </Drawer>
  );
}

ResponsiveDrawer.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};
