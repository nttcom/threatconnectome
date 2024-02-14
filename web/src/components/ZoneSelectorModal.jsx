import { AddBox as AddBoxIcon, Search as SearchIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogContent,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  TextField,
  Typography,
} from "@mui/material";
import { blue } from "@mui/material/colors";
import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { FixedSizeList } from "react-window";

import { getAuthorizedZones } from "../slices/user";
import { modalCommonButtonStyle } from "../utils/const";

function ZoneSelector(props) {
  const { currentZoneNames, onApply, onCancel } = props;

  const [search, setSearch] = useState("");
  const [selectedZoneNames, setSelectedZoneNames] = useState(currentZoneNames);
  const myZones = useSelector((state) => state.user.zones);
  const dispatch = useDispatch();

  useEffect(() => {
    if (myZones === undefined) {
      dispatch(getAuthorizedZones());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!myZones) return <></>;

  const fixedSearch = search.trim();
  const appliableZoneNames = myZones.apply.map((zone) => zone.zone_name);
  const readOnlyZoneNames = currentZoneNames.filter(
    (zoneName) => !appliableZoneNames.includes(zoneName),
  );
  const allZoneNames = [...new Set([...appliableZoneNames, ...readOnlyZoneNames])]
    .filter((zoneName) => zoneName.includes(fixedSearch))
    .sort();

  const handleApply = () => onApply(selectedZoneNames);

  const zoneRow = ({ index, style }) => {
    const zoneName = allZoneNames[index];
    const archived = myZones.apply.find((x) => x.zone_name === zoneName)?.archived ?? false;
    const checked = selectedZoneNames.includes(zoneName);
    const readOnly = readOnlyZoneNames.includes(zoneName) || (!checked && archived);
    const onChange = checked
      ? () => setSelectedZoneNames(selectedZoneNames.filter((x) => x !== zoneName))
      : () => setSelectedZoneNames([...selectedZoneNames, zoneName]);

    return (
      <ListItem style={{ minWidth: "500px" }} disablePadding>
        <ListItemButton edge="start" disableGutters sx={{ py: 0 }}>
          <ListItemIcon>
            <Checkbox checked={checked} disabled={readOnly} onChange={onChange} />
          </ListItemIcon>
          <ListItemText
            primary={zoneName + (archived ? " (ARCHIVED)" : "")}
            primaryTypographyProps={{
              style: {
                whiteSpace: "nowrap",
                overflow: "auto",
                textOverflow: "ellipsis",
              },
            }}
          />
        </ListItemButton>
      </ListItem>
    );
  };

  return (
    <Box sx={{ display: "flex" }}>
      <Box display="flex" flexDirection="column">
        <Typography fontWeight={900} mb={2}>
          Select Zone
        </Typography>
        <Box display="flex" flexDirection="row" alignItems="center" sx={{ ml: "10px" }}>
          <SearchIcon sx={{ mt: 1.5 }} />
          <TextField
            label="Search"
            variant="standard"
            value={search}
            size="small"
            onChange={(event) => setSearch(event.target.value)}
          />
        </Box>
        <Box
          display="flex"
          flexDirection="column"
          flexGrow={1}
          alignItems="left"
          sx={{ overflowY: "auto", border: 1, m: 1, p: 1 }}
        >
          <FixedSizeList height={400} itemSize={35} itemCount={allZoneNames.length}>
            {zoneRow}
          </FixedSizeList>
        </Box>
        <Box display="flex" flexDirection="row">
          <Box flexGrow={1} />
          <Button onClick={() => onCancel()} sx={{ ...modalCommonButtonStyle, mr: 1 }}>
            Cancel
          </Button>
          <Button onClick={handleApply} sx={{ ...modalCommonButtonStyle, mr: 1 }}>
            Apply
          </Button>
        </Box>
      </Box>
    </Box>
  );
}

ZoneSelector.propTypes = {
  currentZoneNames: PropTypes.array.isRequired,
  onApply: PropTypes.func,
  onCancel: PropTypes.func,
};

export function ZoneSelectorModal(props) {
  const { currentZoneNames, onApply } = props;
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <IconButton onClick={() => setModalOpen(true)} sx={{ color: blue[700] }}>
        <AddBoxIcon />
      </IconButton>
      <Dialog open={modalOpen} onClose={() => setModalOpen(false)}>
        <DialogContent>
          <ZoneSelector
            currentZoneNames={currentZoneNames}
            onCancel={() => setModalOpen(false)}
            onApply={(ary) => {
              onApply(ary);
              setModalOpen(false);
            }}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}

ZoneSelectorModal.propTypes = {
  currentZoneNames: PropTypes.array.isRequired,
  onApply: PropTypes.func,
};
