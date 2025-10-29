import {
  List,
  ListItemButton,
  ListItemText,
  Typography,
  Box,
  Grid,
  Chip,
  Avatar,
  AvatarGroup,
  Tooltip,
} from "@mui/material";

// --- ヘルパーコンポーネント ---

// SSVCの優先度に応じて色分けするチップ
const SSVCPriorityChip = ({ priority }) => {
  const styles = {
    immediate: { bgcolor: "#d32f2f", color: "white" },
    high: { bgcolor: "#f57c00", color: "white" },
    medium: { bgcolor: "#fbc02d", color: "black" },
    low: { bgcolor: "#388e3c", color: "white" },
  };
  return <Chip label={priority} size="small" sx={styles[priority] || {}} />;
};

// ユーザー名の頭文字からアバターを生成
const stringToColor = (string) => {
  let hash = 0,
    i,
    chr;
  if (string.length === 0) return "#000000";
  for (i = 0; i < string.length; i++) {
    chr = string.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0;
  }
  let color = "#";
  for (i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xff;
    color += ("00" + value.toString(16)).slice(-2);
  }
  return color;
};

const stringAvatar = (name) => ({
  sx: {
    bgcolor: stringToColor(name),
    width: 24,
    height: 24,
    fontSize: "0.75rem",
  },
  children: name
    .split(" ")
    .map((n) => n[0])
    .join(""),
});

// --- メインコンポーネント ---
/**
 * propsで渡されたタスクのリストを表示するだけのシンプルなコンポーネント
 */
export default function TaskList({ tasks, selectedTaskId, onSelect, members }) {
  return (
    <Box sx={{ p: 1 }}>
      <Typography variant="h6" sx={{ fontWeight: "bold", mb: 1, px: 1, fontSize: "1.1rem" }}>
        Tasks
      </Typography>
      <List component="nav" dense>
        {tasks.map((task) => {
          const isSelected = selectedTaskId === task.ticket_id;
          const assignees = members.filter((m) => (task.assignees || []).includes(m.id));

          return (
            <ListItemButton
              key={task.ticket_id}
              selected={isSelected}
              onClick={() => onSelect(task.ticket_id)}
              sx={{ borderRadius: 2, mb: 0.5 }}
            >
              <ListItemText
                primary={
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: "medium",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {task.target}
                  </Typography>
                }
                secondary={
                  <Grid container alignItems="center" spacing={1} sx={{ mt: 0.5 }}>
                    <Grid item>
                      <SSVCPriorityChip priority={task.ssvc} />
                    </Grid>
                    <Grid item>
                      <Chip label={task.ticket_handling_status} size="small" variant="outlined" />
                    </Grid>
                    <Grid item xs />
                    <Grid item>
                      <AvatarGroup
                        max={4}
                        sx={{ "& .MuiAvatar-root": { width: 24, height: 24, fontSize: "0.75rem" } }}
                      >
                        {assignees.map((a) => (
                          <Tooltip key={a.id} title={a.name}>
                            <Avatar {...stringAvatar(a.name)} />
                          </Tooltip>
                        ))}
                      </AvatarGroup>
                    </Grid>
                  </Grid>
                }
              />
            </ListItemButton>
          );
        })}
      </List>
    </Box>
  );
}
