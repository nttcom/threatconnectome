import { Box } from "@mui/material";
import PropTypes from "prop-types";

export function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <Box
      aria-labelledby={`tab-${index}`}
      hidden={value !== index}
      id={`tab-panel-${index}`}
      m={2}
      role="tabpanel"
      {...other}
    >
      {value === index && children}
    </Box>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};
