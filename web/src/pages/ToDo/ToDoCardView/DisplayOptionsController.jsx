import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined"; // 👈 追加
import FingerprintIcon from "@mui/icons-material/Fingerprint";
import FlagOutlinedIcon from "@mui/icons-material/FlagOutlined";
import GroupOutlinedIcon from "@mui/icons-material/GroupOutlined";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined"; // 👈 追加
import TuneIcon from "@mui/icons-material/Tune";
import {
  Box,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import SwipeableDrawer from "@mui/material/SwipeableDrawer";
import PropTypes from "prop-types";
import { useState } from "react";
import { useTranslation } from "react-i18next";

const sortableKeys = [
  { key: "cve_id", label: "CVE", icon: <FingerprintIcon /> },
  { key: "pteam_name", label: "Team", icon: <GroupOutlinedIcon /> },
  { key: "service_name", label: "Service", icon: <DnsOutlinedIcon /> },
  { key: "package_name", label: "Package", icon: <Inventory2OutlinedIcon /> },
  { key: "ssvc_deployer_priority", label: "SSVC", icon: <FlagOutlinedIcon /> },
];

export function DisplayOptionsController({
  sortConfig,
  onSortConfigChange,
  itemsPerPage,
  onItemsPerPageChange,
}) {
  const { t } = useTranslation("toDo", { keyPrefix: "ToDoCardView.DisplayOptionsController" });
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleSortKeyChange = (key) => {
    onSortConfigChange({ ...sortConfig, key });
  };

  const handleSortDirectionChange = (event, newDirection) => {
    if (newDirection !== null) {
      onSortConfigChange({ ...sortConfig, direction: newDirection });
    }
  };

  const handleItemsPerPageChange = (event, newValue) => {
    if (newValue !== null) {
      onItemsPerPageChange(newValue);
    }
  };

  return (
    <>
      <Tooltip title={t("tooltip")}>
        <IconButton
          onClick={() => setIsDrawerOpen(true)}
          sx={{
            border: "1px solid",
            borderColor: "grey.300",
            borderRadius: 2,
            "&:hover": {
              backgroundColor: "grey.100",
            },
          }}
        >
          <TuneIcon />
        </IconButton>
      </Tooltip>

      <SwipeableDrawer
        anchor="bottom"
        open={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        // The onOpen prop is required by SwipeableDrawer.
        // Pass an empty function to satisfy the requirement and prevent prop-type warnings,
        // as the swipe-to-open functionality is not used in this implementation.
        onOpen={() => {}}
        // Disable the swipe-to-open gesture explicitly as it's not part of the spec.
        disableDiscovery
        slotProps={{ paper: { sx: { borderTopLeftRadius: 16, borderTopRightRadius: 16 } } }}
      >
        <Box sx={{ p: 2, pb: 3 }}>
          <Box
            sx={{
              width: 40,
              height: 5,
              backgroundColor: "grey.300",
              borderRadius: 3,
              mx: "auto",
              mb: 2,
            }}
          />
          <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
            {t("title")}
          </Typography>

          <Typography variant="overline" color="text.secondary">
            {t("sortBy")}
          </Typography>
          <ToggleButtonGroup
            value={sortConfig.direction}
            exclusive
            fullWidth
            onChange={handleSortDirectionChange}
            sx={{ mb: 1 }}
          >
            <ToggleButton value="asc">
              <ArrowUpwardIcon sx={{ mr: 1 }} />
              {t("ascending")}
            </ToggleButton>
            <ToggleButton value="desc">
              <ArrowDownwardIcon sx={{ mr: 1 }} />
              {t("descending")}
            </ToggleButton>
          </ToggleButtonGroup>
          <List>
            {sortableKeys.map((item) => (
              <ListItem key={item.key} disablePadding>
                <ListItemButton
                  selected={sortConfig.key === item.key}
                  onClick={() => handleSortKeyChange(item.key)}
                  sx={{ py: 1.5 }}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={t(item.key)} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          <Typography variant="overline" color="text.secondary">
            {t("rowsPerPage")}
          </Typography>
          <ToggleButtonGroup
            value={itemsPerPage}
            exclusive
            fullWidth
            onChange={handleItemsPerPageChange}
          >
            {[10, 25, 50].map((option) => (
              <ToggleButton key={option} value={option}>
                {option}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>
      </SwipeableDrawer>
    </>
  );
}

DisplayOptionsController.propTypes = {
  sortConfig: PropTypes.object.isRequired,
  onSortConfigChange: PropTypes.func.isRequired,
  itemsPerPage: PropTypes.number.isRequired,
  onItemsPerPageChange: PropTypes.func.isRequired,
};
