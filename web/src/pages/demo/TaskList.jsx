import { List, ListItemButton, ListItemText, Typography, Box } from "@mui/material";

const StatusBadge = ({ status }) => {
  const statusStyles = {
    "In Progress": { bgcolor: "primary.main" },
    Alerted: { bgcolor: "warning.main" },
    Open: { bgcolor: "grey.500" },
    Resolved: { bgcolor: "success.main" },
  };
  return (
    <Box
      component="span"
      sx={{
        height: 8,
        width: 8,
        borderRadius: "50%",
        display: "inline-block",
        mr: 1,
        ...statusStyles[status],
      }}
    />
  );
};

/**
 * タスクリストコンポーネント
 * @param {object} props
 * @param {Array<object>} props.tasks - 表示するタスクのリスト
 * @param {string} props.selectedTaskId - 現在選択されているタスクのID
 * @param {Function} props.onSelect - タスクが選択されたときに呼ばれる関数
 */
export default function TaskList({ tasks, selectedTaskId, onSelect }) {
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ fontWeight: "bold", mb: 1, fontSize: "1.1rem" }}>
        Tasks
      </Typography>
      <List component="nav" dense>
        {tasks.map((task) => (
          <ListItemButton
            key={task.ticket_id}
            selected={selectedTaskId === task.ticket_id}
            onClick={() => onSelect(task.ticket_id)}
            sx={{
              borderRadius: 2,
              "&.Mui-selected": {
                bgcolor: "primary.main",
                color: "white",
                "&:hover": { bgcolor: "primary.dark" },
              },
            }}
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
                <Box component="span" sx={{ display: "flex", alignItems: "center", mt: 0.5 }}>
                  <StatusBadge status={task.ticket_handling_status} />
                  <Typography
                    variant="caption"
                    sx={{
                      color: selectedTaskId === task.ticket_id ? "inherit" : "text.secondary",
                    }}
                  >
                    {task.ticket_handling_status}
                  </Typography>
                </Box>
              }
            />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
}
