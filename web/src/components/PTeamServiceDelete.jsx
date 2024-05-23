import {
  Box,
  Button,
  Checkbox,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import React from "react";
import { useSelector } from "react-redux";

import styles from "../cssModule/dialog.module.css";

export function PTeamServiceDelete() {
  const [checked, setChecked] = React.useState([0]);

  const groups = useSelector((state) => state.pteam.groups);

  const handleToggle = (value) => () => {
    const currentIndex = checked.indexOf(value);
    const newChecked = [...checked];

    if (currentIndex === -1) {
      newChecked.push(value);
    } else {
      newChecked.splice(currentIndex, 1);
    }

    setChecked(newChecked);
  };

  return (
    <Box>
      <List
        sx={{
          width: "98%",
          position: "relative",
          overflow: "auto",
          maxHeight: 200,
        }}
      >
        {groups.map((group) => {
          const labelId = `checkbox-list-label-${group}`;
          return (
            <ListItem key={group} disablePadding>
              <ListItemButton role={undefined} onClick={handleToggle(group)} dense>
                <ListItemIcon>
                  <Checkbox
                    edge="start"
                    checked={checked.indexOf(group) !== -1}
                    tabIndex={-1}
                    disableRipple
                    inputProps={{ "aria-labelledby": labelId }}
                  />
                </ListItemIcon>
                <ListItemText id={labelId} primary={group} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      <Divider sx={{ mt: 5 }} />
      <Box display="flex" mt={2}>
        <Box flexGrow={1} />
        <Button className={styles.delete_bg_btn}>Delete</Button>
      </Box>
    </Box>
  );
}
