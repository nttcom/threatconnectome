import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Typography,
  Box,
  Select,
  MenuItem,
  Collapse,
  Grid,
  Autocomplete,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Link,
} from "@mui/material";

// --- ヘルパーコンポーネント (変更なし) ---
const SafetyImpactSelector = ({ value, onChange }) => (
  <Select fullWidth size="small" value={value} onChange={onChange}>
    <MenuItem value="Catastrophic">Catastrophic</MenuItem>
    <MenuItem value="High">High</MenuItem>
    <MenuItem value="Medium">Medium</MenuItem>
  </Select>
);
const StatusSelector = ({ value, onChange }) => (
  <Select fullWidth size="small" value={value} onChange={onChange}>
    <MenuItem value="Acknowledge">Acknowledge</MenuItem>
    <MenuItem value="Schedule">Schedule</MenuItem>
    <MenuItem value="Complete">Complete</MenuItem>
  </Select>
);
const AssigneesSelector = ({ value, onChange, members }) => (
  <Autocomplete
    multiple
    options={members}
    getOptionLabel={(option) => option.name}
    value={members.filter((m) => (value || []).includes(m.id))}
    onChange={(event, newValue) => onChange(newValue.map((item) => item.id))}
    renderInput={(params) => <TextField {...params} size="small" placeholder="Select members" />}
  />
);

// --- メインコンポーネント ---
export default function TaskEditor({ task, members, onUpdate, vulnerability }) {
  if (!task) {
    return (
      <Box p={3} display="flex" alignItems="center" justifyContent="center" height="100%">
        <Typography color="text.secondary">[translate:Select a task to view details]</Typography>
      </Box>
    );
  }

  const formattedDueDate = task.due_date ? task.due_date.slice(0, 10) : "";

  // デバッグ用の return 文を削除

  return (
    <Box sx={{ p: 3 }}>
      {/* --- 編集フォーム --- */}
      <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
        Edit Task
      </Typography>

      <Box mb={2}>
        <Typography variant="overline" color="text.secondary">
          Target
        </Typography>
        <Typography>{task.target}</Typography>
      </Box>

      <Box mb={2}>
        <Typography variant="overline" color="text.secondary">
          Safety Impact
        </Typography>
        <SafetyImpactSelector
          value={task.safety_impact || ""}
          onChange={(e) => onUpdate("safety_impact", e.target.value)}
        />
      </Box>

      <Box mb={2}>
        <Typography variant="overline" color="text.secondary">
          Status
        </Typography>
        <StatusSelector
          value={task.ticket_handling_status || ""}
          onChange={(e) => onUpdate("ticket_handling_status", e.target.value)}
        />
      </Box>

      <Collapse in={task.ticket_handling_status === "Schedule"}>
        <Box mb={2}>
          <Typography variant="overline" color="text.secondary">
            Due Date
          </Typography>
          <TextField
            fullWidth
            size="small"
            type="date"
            value={formattedDueDate}
            onChange={(e) =>
              onUpdate("due_date", e.target.value ? new Date(e.target.value).toISOString() : null)
            }
            InputLabelProps={{ shrink: true }}
          />
        </Box>
      </Collapse>

      <Box mb={4}>
        {" "}
        {/* 最後の要素なので少し多めにマージンを取る */}
        <Typography variant="overline" color="text.secondary">
          Assignees
        </Typography>
        <AssigneesSelector
          value={task.assignees}
          members={members}
          onChange={(ids) => onUpdate("assignees", ids)}
        />
      </Box>

      {/* --- 詳細情報 --- */}
      <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
        Vulnerability Details
      </Typography>

      {/* <div>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>CVE Information</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2">
              <strong>CVE ID:</strong>{" "}
              <Link
                href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${vulnerability.cveId}`}
                target="_blank"
              >
                {vulnerability.cveId || "N/A"}
              </Link>
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              {vulnerability.description || "No description."}
            </Typography>
          </AccordionDetails>
        </Accordion>
      </div> */}

      {/* <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Version Information</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2">
            <strong>Affected Versions:</strong>{" "}
            {vulnerability.affected_versions?.join(", ") || "N/A"}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            <strong>Patched Versions:</strong> {vulnerability.patched_versions?.join(", ") || "N/A"}
          </Typography>
        </AccordionDetails>
      </Accordion> */}

      {/* <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography>Mitigation</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
            {vulnerability.mitigation || "No mitigation advice."}
          </Typography>
        </AccordionDetails>
      </Accordion> */}
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={4}>
        {/* --- 左側: 編集フォーム --- */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
            Edit Task
          </Typography>

          <Box mb={2}>
            <Typography variant="overline" color="text.secondary">
              Target
            </Typography>
            <Typography>{task.target}</Typography>
          </Box>
          <Box mb={2}>
            <Typography variant="overline" color="text.secondary">
              Safety Impact
            </Typography>
            <SafetyImpactSelector
              value={task.safety_impact || ""}
              onChange={(e) => onUpdate("safety_impact", e.target.value)}
            />
          </Box>
          <Box mb={2}>
            <Typography variant="overline" color="text.secondary">
              Status
            </Typography>
            <StatusSelector
              value={task.ticket_handling_status || ""}
              onChange={(e) => onUpdate("ticket_handling_status", e.target.value)}
            />
          </Box>

          <Collapse in={task.ticket_handling_status === "Schedule"}>
            <Box mb={2}>
              <Typography variant="overline" color="text.secondary">
                Due Date
              </Typography>
              <TextField
                fullWidth
                size="small"
                type="date"
                value={formattedDueDate}
                onChange={(e) =>
                  onUpdate(
                    "due_date",
                    e.target.value ? new Date(e.target.value).toISOString() : null,
                  )
                }
                InputLabelProps={{ shrink: true }}
              />
            </Box>
          </Collapse>

          <Box>
            <Typography variant="overline" color="text.secondary">
              Assignees
            </Typography>
            <AssigneesSelector
              value={task.assignees}
              members={members}
              onChange={(ids) => onUpdate("assignees", ids)}
            />
          </Box>
        </Grid>

        {/* --- 右側: 詳細情報 --- */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
            Vulnerability Details
          </Typography>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>CVE Information</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2">
                <strong>CVE ID:</strong>{" "}
                <Link
                  href={`https://cve.mitre.org/cgi-bin/cvename.cgi?name=${vulnerability.cveId}`}
                  target="_blank"
                >
                  {vulnerability.cveId || "N/A"}
                </Link>
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                {vulnerability.description || "No description."}
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Version Information</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2">
                <strong>Affected Versions:</strong>{" "}
                {vulnerability.affected_versions?.join(", ") || "N/A"}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Patched Versions:</strong>{" "}
                {vulnerability.patched_versions?.join(", ") || "N/A"}
              </Typography>
            </AccordionDetails>
          </Accordion>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Mitigation</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
                {vulnerability.mitigation || "No mitigation advice."}
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>
    </Box>
  );
}
