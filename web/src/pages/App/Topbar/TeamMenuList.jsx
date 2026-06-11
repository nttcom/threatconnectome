import AddIcon from "@mui/icons-material/Add";
import { Box, Divider, ListItemIcon, ListItemText, MenuItem } from "@mui/material";

import { TeamMenuItem } from "./TeamMenuItem";
import { compactMenuItemSx, teamMenuListSx } from "./topbarStyles";

export function TeamMenuList({ labels, onCreateTeam, onSelectTeam, teamItems }) {
  const selectTeam = (teamId) => {
    onSelectTeam(teamId);
  };

  return (
    <>
      <Box sx={teamMenuListSx}>
        {teamItems.map((item) => (
          <TeamMenuItem key={item.id} item={item} onSelectTeam={selectTeam} />
        ))}
      </Box>
      <Divider sx={{ my: 0.75 }} />
      <MenuItem onClick={onCreateTeam} sx={compactMenuItemSx}>
        <ListItemIcon>
          <AddIcon fontSize="small" />
        </ListItemIcon>
        <ListItemText>{labels.createTeam}</ListItemText>
      </MenuItem>
    </>
  );
}
