import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import { Typography, Box, Select, MenuItem, Collapse } from "@mui/material";

// --- セレクターコンポーネント ---
const SafetyImpactSelector = ({ value, onChange }) => (
  <Select fullWidth size="small" value={value} onChange={onChange}>
    <MenuItem value="Catastrophic">Catastrophic</MenuItem>
    <MenuItem value="High">High</MenuItem>
    <MenuItem value="Medium">Medium</MenuItem>
  </Select>
);

const TicketHandlingStatusSelector = ({ value, onChange }) => (
  <Select fullWidth size="small" value={value} onChange={onChange}>
    <MenuItem value="Open">Open</MenuItem>
    <MenuItem value="In Progress">In Progress</MenuItem>
    <MenuItem value="Alerted">Alerted</MenuItem>
    <MenuItem value="Resolved">Resolved</MenuItem>
  </Select>
);

const AssigneesSelector = ({ value, onChange, members }) => (
  <Select fullWidth size="small" value={value || ""} onChange={onChange}>
    {members.map((m) => (
      <MenuItem key={m.id} value={m.id}>
        {m.name}
      </MenuItem>
    ))}
  </Select>
);

/**
 * タスク編集フォームコンポーネント
 * @param {object} props
 * @param {object} props.task - 編集対象のタスク
 * @param {Array<object>} props.members - チームメンバーのリスト
 * @param {Function} props.onUpdate - タスク情報が更新されたときに呼ばれる関数
 * @param {boolean} props.isReasonOpen - 理由表示エリアの開閉状態
 * @param {Function} props.onToggleReason - 理由表示エリアの開閉を切り替える関数
 */
export default function TaskEditor({ task, members, onUpdate, isReasonOpen, onToggleReason }) {
  if (!task) {
    return (
      <Box p={3} display="flex" alignItems="center" justifyContent="center" height="100%">
        <Typography color="text.secondary">Select a task to view details</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" sx={{ fontWeight: "bold", mb: 3 }}>
        Edit Task
      </Typography>

      {/* Safety Impact */}
      <Box>
        <Box
          onClick={() => task.safety_impact_change_reason && onToggleReason()}
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            cursor: task.safety_impact_change_reason ? "pointer" : "default",
          }}
        >
          <Typography variant="overline" display="block" color="text.secondary">
            Safety Impact
          </Typography>
          {task.safety_impact_change_reason && (
            <KeyboardArrowDownIcon
              sx={{
                transform: isReasonOpen ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.2s",
              }}
            />
          )}
        </Box>
        <SafetyImpactSelector
          value={task.safety_impact}
          onChange={(e) => onUpdate("safety_impact", e.target.value)}
        />
        <Collapse in={isReasonOpen} timeout="auto" unmountOnExit>
          <Box
            sx={{
              mt: 1,
              maxHeight: 150,
              overflowY: "auto",
              p: 2,
              bgcolor: "grey.100",
              borderRadius: 2,
            }}
          >
            <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
              {task.safety_impact_change_reason}
            </Typography>
          </Box>
        </Collapse>
      </Box>

      {/* Status */}
      <Typography variant="overline" display="block" color="text.secondary" mt={2}>
        Status
      </Typography>
      <TicketHandlingStatusSelector
        value={task.ticket_handling_status}
        onChange={(e) => onUpdate("ticket_handling_status", e.target.value)}
      />

      {/* Assignees */}
      <Typography variant="overline" display="block" color="text.secondary" mt={2}>
        Assignees
      </Typography>
      <AssigneesSelector
        value={task.assignees[0]}
        members={members}
        onChange={(e) => onUpdate("assignees", [e.target.value])}
      />
    </Box>
  );
}
