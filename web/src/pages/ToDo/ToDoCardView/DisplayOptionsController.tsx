import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import FingerprintIcon from "@mui/icons-material/Fingerprint";
import FlagOutlinedIcon from "@mui/icons-material/FlagOutlined";
import GroupOutlinedIcon from "@mui/icons-material/GroupOutlined";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
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
import type { MouseEvent, ReactNode } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import type { SortConfig } from "../../../hooks/ToDo/useTodoState";

const sortableKeys: Array<{ key: string; icon: ReactNode }> = [
  { key: "cve_id", icon: <FingerprintIcon /> },
  { key: "pteam_name", icon: <GroupOutlinedIcon /> },
  { key: "service_name", icon: <DnsOutlinedIcon /> },
  { key: "package_name", icon: <Inventory2OutlinedIcon /> },
  { key: "ssvc_deployer_priority", icon: <FlagOutlinedIcon /> },
];

type DisplayOptionsControllerProps = {
  sortConfig: SortConfig;
  onSortConfigChange: (newConfig: SortConfig) => void;
  itemsPerPage: number;
  onItemsPerPageChange: (newValue: number) => void;
};

export function DisplayOptionsController({
  sortConfig,
  onSortConfigChange,
  itemsPerPage,
  onItemsPerPageChange,
}: DisplayOptionsControllerProps) {
  const { t } = useTranslation("toDo", { keyPrefix: "ToDoCardView.DisplayOptionsController" });
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleSortKeyChange = (key: string) => {
    onSortConfigChange({ ...sortConfig, key });
  };

  const handleSortDirectionChange = (
    _event: MouseEvent<HTMLElement>,
    newDirection: string | null,
  ) => {
    if (newDirection === "asc" || newDirection === "desc") {
      onSortConfigChange({ ...sortConfig, direction: newDirection });
    }
  };

  const handleItemsPerPageChange = (_event: MouseEvent<HTMLElement>, newValue: number | null) => {
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
