/* eslint-disable @cspell/spellchecker, react/prop-types */
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import BugReportRoundedIcon from "@mui/icons-material/BugReportRounded";
import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import FolderOpenRoundedIcon from "@mui/icons-material/FolderOpenRounded";
import ManageSearchRoundedIcon from "@mui/icons-material/ManageSearchRounded";
import RouteRoundedIcon from "@mui/icons-material/RouteRounded";
import {
  Box,
  Button,
  Chip,
  Divider,
  Grid,
  LinearProgress,
  Paper,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Typography,
} from "@mui/material";
import { alpha } from "@mui/material/styles";
import { useMemo, useState } from "react";

if (!import.meta.env.VITE_AUTH_SERVICE) {
  import.meta.env.VITE_AUTH_SERVICE = "firebase";
}

const sbomEntries = [
  {
    bomRef: "pkg:npm/lodash@4.17.20#web-app",
    ecosystem: "npm",
    fixable: 18,
    fixed: "4.17.21+",
    investigate: 4,
    location: "web-app / package.json",
    name: "lodash",
    notAffected: 2,
    occurrenceId: "web-lodash",
    pathHtml: "web-app<br>└─ lodash 4.17.20",
    project: "web-app",
    recommendAction: "4.17.21以上へ更新",
    recommendDescription: "この更新で 18 / 24件 の脆弱性を解消できます。",
    recommendTitle: "4.17.21以上へ更新してください",
    responseLabel: "修正版あり",
    responseTone: "emerald",
    safetyImpact: "negligible",
    ssvcDecision: "Immediate",
    ssvcFactors: {
      automatable: "Yes",
      exploitation: "Public PoC",
      humanImpact: "Medium",
      systemExposure: "Open",
    },
    ssvcReason:
      "公開PoCがあり、本番系での露出と自動化可能性を考慮して、通常サイクルを待たずに対応します。",
    ssvcTone: "rose",
    todos: [
      "package.json の lodash を 4.17.21 以上に更新",
      "lockfileを再生成",
      "単体テスト・依存テストを実行",
      "PRを作成してレビュー依頼",
    ],
    total: 24,
    type: "直接依存",
    version: "4.17.20",
  },
  {
    bomRef: "pkg:npm/lodash@4.17.20#worker",
    ecosystem: "npm",
    fixable: 18,
    fixed: "4.17.21+",
    investigate: 4,
    location: "worker / package.json",
    name: "lodash",
    notAffected: 2,
    occurrenceId: "worker-lodash",
    pathHtml: "worker<br>└─ lodash 4.17.20",
    project: "worker",
    recommendAction: "4.17.21以上へ更新",
    recommendDescription: "この更新で 18 / 24件 の脆弱性を解消できます。",
    recommendTitle: "4.17.21以上へ更新してください",
    responseLabel: "修正版あり",
    responseTone: "emerald",
    safetyImpact: "negligible",
    ssvcDecision: "Immediate",
    ssvcFactors: {
      automatable: "Yes",
      exploitation: "Public PoC",
      humanImpact: "Medium",
      systemExposure: "Open",
    },
    ssvcReason:
      "公開PoCがあり、本番系での露出と自動化可能性を考慮して、通常サイクルを待たずに対応します。",
    ssvcTone: "rose",
    todos: [
      "package.json の lodash を 4.17.21 以上に更新",
      "lockfileを再生成",
      "単体テスト・依存テストを実行",
      "PRを作成してレビュー依頼",
    ],
    total: 24,
    type: "直接依存",
    version: "4.17.20",
  },
  {
    bomRef: "pkg:maven/org.springframework/spring-core@5.3.18#api-service",
    ecosystem: "Maven",
    fixable: 48,
    fixed: "5.3.33+",
    investigate: 10,
    location: "api-service / pom.xml",
    name: "spring-core",
    notAffected: 6,
    occurrenceId: "api-spring-core",
    pathHtml:
      "api-service<br>└─ spring-boot-starter-web 2.6.6<br>&nbsp;&nbsp;&nbsp;└─ spring-core 5.3.18",
    project: "api-service",
    recommendAction: "spring-boot-starter-web更新",
    recommendDescription: "spring-boot-starter-webを更新すると 48 / 64件 の脆弱性を解消できます。",
    recommendTitle: "親コンポーネントを更新してください",
    responseLabel: "親更新で対応",
    responseTone: "emerald",
    safetyImpact: "moderate",
    ssvcDecision: "Out-of-Cycle",
    ssvcFactors: {
      automatable: "No",
      exploitation: "Public PoC",
      humanImpact: "Medium",
      systemExposure: "Controlled",
    },
    ssvcReason:
      "公開PoCがあり、推移的依存として本番影響が残るため、通常メンテナンスより前倒しで親コンポーネント更新を進めます。",
    ssvcTone: "amber",
    todos: [
      "spring-boot-starter-web の更新可能バージョンを確認",
      "依存解決後の spring-core バージョンを確認",
      "統合テストを実行",
      "残る脆弱性はVEX判断または例外登録",
    ],
    total: 64,
    type: "推移的依存",
    version: "5.3.18",
  },
  {
    bomRef: "pkg:maven/org.springframework/spring-core@5.3.18#batch-service",
    ecosystem: "Maven",
    fixable: 48,
    fixed: "5.3.33+",
    investigate: 10,
    location: "batch-service / pom.xml",
    name: "spring-core",
    notAffected: 6,
    occurrenceId: "batch-spring-core",
    pathHtml:
      "batch-service<br>└─ spring-batch-core 4.3.6<br>&nbsp;&nbsp;&nbsp;└─ spring-core 5.3.18",
    project: "batch-service",
    recommendAction: "spring-boot-starter-web更新",
    recommendDescription: "spring-boot-starter-webを更新すると 48 / 64件 の脆弱性を解消できます。",
    recommendTitle: "親コンポーネントを更新してください",
    responseLabel: "親更新で対応",
    responseTone: "emerald",
    safetyImpact: "moderate",
    ssvcDecision: "Out-of-Cycle",
    ssvcFactors: {
      automatable: "No",
      exploitation: "Public PoC",
      humanImpact: "Medium",
      systemExposure: "Controlled",
    },
    ssvcReason:
      "公開PoCがあり、推移的依存として本番影響が残るため、通常メンテナンスより前倒しで親コンポーネント更新を進めます。",
    ssvcTone: "amber",
    todos: [
      "spring-boot-starter-web の更新可能バージョンを確認",
      "依存解決後の spring-core バージョンを確認",
      "統合テストを実行",
      "残る脆弱性はVEX判断または例外登録",
    ],
    total: 64,
    type: "推移的依存",
    version: "5.3.18",
  },
  {
    bomRef: "pkg:deb/debian/openssl@1.1.1n#api-runtime",
    ecosystem: "Debian",
    fixable: 0,
    fixed: "ベースイメージ更新",
    investigate: 11,
    location: "api-runtime / Docker image",
    name: "openssl",
    notAffected: 0,
    occurrenceId: "runtime-openssl",
    pathHtml: "api-runtime image<br>└─ debian:bullseye<br>&nbsp;&nbsp;&nbsp;└─ openssl 1.1.1n",
    project: "api-runtime",
    recommendAction: "ベースイメージ更新を確認",
    recommendDescription:
      "コンテナイメージ由来のため、パッケージ単体ではなくベースイメージの更新で確認します。",
    recommendTitle: "ベースイメージ更新を確認してください",
    responseLabel: "確認が必要",
    responseTone: "amber",
    safetyImpact: "low",
    ssvcDecision: "Scheduled",
    ssvcFactors: {
      automatable: "No",
      exploitation: "None",
      humanImpact: "Low",
      systemExposure: "Controlled",
    },
    ssvcReason:
      "悪用確認はなく、OSパッケージ由来でベースイメージ更新の確認が必要なため、定期メンテナンス枠で扱います。",
    ssvcTone: "blue",
    todos: [
      "DockerfileのFROMイメージを確認",
      "新しいベースイメージでSBOMを再生成",
      "ランタイム互換性を確認",
      "残る脆弱性をディストリビューションの修正状況で確認",
    ],
    total: 11,
    type: "OS package",
    version: "1.1.1n",
  },
  {
    bomRef: "pkg:npm/ansi-regex@3.0.0#admin",
    ecosystem: "npm",
    fixable: 0,
    fixed: "例外期限 2026-09-30",
    investigate: 2,
    location: "admin / package-lock.json",
    name: "ansi-regex",
    notAffected: 5,
    occurrenceId: "admin-ansi-regex",
    pathHtml: "admin<br>└─ eslint 6.8.0<br>&nbsp;&nbsp;&nbsp;└─ ansi-regex 3.0.0",
    project: "admin",
    recommendAction: "延期理由を記録",
    recommendDescription:
      "本番利用条件では影響が低いため、利用経路と再評価期限を残して監視します。",
    recommendTitle: "延期理由と再評価期限を記録してください",
    responseLabel: "期限付き例外",
    responseTone: "slate",
    safetyImpact: "negligible",
    ssvcDecision: "Defer",
    ssvcFactors: {
      automatable: "No",
      exploitation: "None",
      humanImpact: "Low",
      systemExposure: "Small",
    },
    ssvcReason: "開発時のみの依存で本番到達性が低いため、期限付きの例外として継続監視します。",
    ssvcTone: "slate",
    todos: [
      "依存経路が開発時のみであることを確認",
      "VEXまたは例外理由を記録",
      "再評価期限を設定",
      "親ツール更新時に再確認",
    ],
    total: 7,
    type: "推移的依存",
    version: "3.0.0",
  },
];

const ssvcDecisionConfig = {
  Defer: { rank: 4 },
  Immediate: { rank: 1 },
  "Out-of-Cycle": { rank: 2 },
  Scheduled: { rank: 3 },
};

const slate = {
  50: "#f8fafc",
  100: "#f1f5f9",
  200: "#e2e8f0",
  300: "#cbd5e1",
  400: "#94a3b8",
  500: "#64748b",
  600: "#475569",
  700: "#334155",
  800: "#1e293b",
  900: "#0f172a",
  950: "#020617",
};

const toneColors = {
  amber: { bg: "#fef3c7", border: "#fcd34d", fg: "#92400e", soft: "#fffbeb" },
  blue: { bg: "#dbeafe", border: "#93c5fd", fg: "#1d4ed8", soft: "#eff6ff" },
  emerald: { bg: "#d1fae5", border: "#6ee7b7", fg: "#047857", soft: "#ecfdf5" },
  rose: { bg: "#ffe4e6", border: "#fda4af", fg: "#be123c", soft: "#fff1f2" },
  slate: { bg: slate[100], border: slate[300], fg: slate[700], soft: slate[50] },
};

const progressLabels = {
  Defer: "延期",
  Immediate: "未着手",
  "Out-of-Cycle": "対応中",
  Scheduled: "調査中",
};

const rootSx = {
  bgcolor: slate[50],
  color: slate[900],
  minHeight: "100vh",
  px: { lg: 3, sm: 2.5, xs: 2 },
  py: { sm: 3, xs: 2 },
};

const pageSx = {
  maxWidth: 1500,
  mx: "auto",
};

const surfaceSx = {
  bgcolor: "white",
  border: `1px solid ${slate[200]}`,
  borderRadius: 2,
  boxShadow: "0 18px 45px rgba(15, 23, 42, 0.08)",
};

const compactButtonSx = {
  borderRadius: 2,
  fontWeight: 700,
  letterSpacing: 0,
  textTransform: "none",
};

function dependencyKey(entry) {
  return [entry.ecosystem, entry.name, entry.version]
    .map((value) => String(value).trim().toLowerCase())
    .join("::");
}

function uniqueJoined(values, separator = " / ") {
  return [...new Set(values.filter(Boolean))].join(separator);
}

function isOsPackage(value) {
  const label = String(value || "");
  return label.includes("OS package") || label.includes("OSパッケージ");
}

function normalizePath(value) {
  return String(value || "")
    .replace(/<br\s*\/?\s*>/gi, "\n")
    .replace(/&nbsp;/g, " ");
}

function groupSbomEntries(entries) {
  const grouped = entries.reduce((acc, entry) => {
    const key = dependencyKey(entry);
    const dependency = acc.get(key) ?? {
      ...entry,
      key,
      occurrences: [],
      safetyImpactValues: [],
      typeValues: [],
    };

    dependency.occurrences.push({
      location: entry.location,
      occurrenceId: entry.occurrenceId,
      path: normalizePath(entry.pathHtml),
      project: entry.project,
      safetyImpact: entry.safetyImpact,
      type: entry.type,
    });
    dependency.safetyImpactValues.push(entry.safetyImpact);
    dependency.typeValues.push(entry.type);
    acc.set(key, dependency);

    return acc;
  }, new Map());

  return [...grouped.values()]
    .map((dependency) => ({
      ...dependency,
      occurrenceCount: dependency.occurrences.length,
      safetyImpact: uniqueJoined(dependency.safetyImpactValues),
      type: uniqueJoined(dependency.typeValues),
    }))
    .sort(
      (a, b) =>
        ssvcDecisionConfig[a.ssvcDecision].rank - ssvcDecisionConfig[b.ssvcDecision].rank ||
        a.name.localeCompare(b.name),
    );
}

function buildVulns(dependency) {
  return Array.from({ length: dependency.total }, (_, index) => {
    const rowNumber = index + 1;
    const status = rowNumber <= dependency.fixable ? "fixable" : "investigate";

    return {
      fixedVersion: status === "fixable" ? dependency.fixed : "確認が必要",
      id:
        rowNumber % 3 === 0
          ? `GHSA-${dependency.name.slice(0, 4)}-${1000 + rowNumber}`
          : `CVE-2026-${String(1000 + rowNumber).padStart(4, "0")}`,
      ssvcDecision: dependency.ssvcDecision,
      ssvcTone: dependency.ssvcTone,
      status,
    };
  });
}

function toneColor(tone) {
  return toneColors[tone] ?? toneColors.slate;
}

function ToneChip({ label, tone = "slate" }) {
  const colors = toneColor(tone);

  return (
    <Chip
      label={label}
      size="small"
      sx={{
        bgcolor: colors.bg,
        border: `1px solid ${colors.border}`,
        borderRadius: 999,
        color: colors.fg,
        fontSize: 12,
        fontWeight: 800,
        height: 26,
        letterSpacing: 0,
      }}
    />
  );
}

function PackageTypeChip({ type }) {
  if (!isOsPackage(type)) {
    return null;
  }

  return <ToneChip label="OSパッケージ" tone="blue" />;
}

function SmallMetric({ label, children }) {
  return (
    <Box
      sx={{
        bgcolor: slate[50],
        borderRadius: 2,
        minWidth: 0,
        px: 1.5,
        py: 1.25,
        textAlign: "center",
      }}
    >
      <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>{label}</Typography>
      <Box sx={{ mt: 0.75, minWidth: 0 }}>{children}</Box>
    </Box>
  );
}

function SummaryPill({ label, tone = "slate", value }) {
  const colors = toneColor(tone);

  return (
    <Box
      component="span"
      sx={{
        alignItems: "center",
        bgcolor: "white",
        border: `1px solid ${colors.border}`,
        borderRadius: 999,
        color: slate[950],
        display: "inline-flex",
        fontSize: 12,
        fontWeight: 800,
        gap: 0.75,
        lineHeight: 1,
        px: 1.5,
        py: 0.75,
        whiteSpace: "nowrap",
      }}
    >
      <Box component="span" sx={{ color: colors.fg }}>
        {label}
      </Box>
      {value}件
    </Box>
  );
}

function ListView({ dependencies, onOpen }) {
  return (
    <Paper elevation={0} sx={{ ...surfaceSx, overflow: "hidden" }}>
      <Box
        sx={{
          bgcolor: slate[50],
          borderBottom: `1px solid ${slate[200]}`,
          color: slate[500],
          display: { md: "grid", xs: "none" },
          fontSize: 12,
          fontWeight: 800,
          gap: 1.5,
          gridTemplateColumns: "minmax(0, 1.5fr) minmax(120px, 1fr) minmax(120px, 1fr) auto",
          px: 2,
          py: 1.5,
        }}
      >
        <Box>コンポーネント</Box>
        <Box>SSVC</Box>
        <Box>ステータス</Box>
        <Box sx={{ textAlign: "right" }}>詳細</Box>
      </Box>

      <Stack divider={<Divider sx={{ borderColor: slate[100] }} />}>
        {dependencies.map((dependency) => (
          <Box
            component="article"
            key={dependency.key}
            sx={{
              display: "grid",
              gap: 1.5,
              gridTemplateColumns: {
                md: "minmax(0, 1.5fr) minmax(120px, 1fr) minmax(120px, 1fr) auto",
                xs: "1fr",
              },
              p: 2,
              transition: "background-color 160ms ease",
              "&:hover": { bgcolor: alpha(slate[50], 0.72) },
            }}
          >
            <Box sx={{ minWidth: 0 }}>
              <Stack direction="row" flexWrap="wrap" gap={1} sx={{ alignItems: "center" }}>
                <Typography
                  component="h2"
                  sx={{
                    color: slate[900],
                    fontSize: 14,
                    fontWeight: 900,
                    letterSpacing: 0,
                    minWidth: 0,
                  }}
                >
                  {dependency.name}
                </Typography>
                <PackageTypeChip type={dependency.type} />
              </Stack>
              <Typography
                sx={{
                  color: slate[500],
                  fontSize: 12,
                  fontWeight: 700,
                  mt: 0.75,
                  wordBreak: "break-word",
                }}
              >
                {dependency.ecosystem} /{" "}
                <Box component="span" sx={{ fontFamily: "monospace" }}>
                  {dependency.version}
                </Box>{" "}
                / {dependency.occurrenceCount}箇所
              </Typography>
            </Box>

            <Box sx={{ alignItems: "center", display: "flex" }}>
              <ToneChip label={dependency.ssvcDecision} tone={dependency.ssvcTone} />
            </Box>

            <Box sx={{ alignItems: "center", display: "flex" }}>
              <ToneChip
                label={progressLabels[dependency.ssvcDecision] ?? "確認中"}
                tone={dependency.responseTone}
              />
            </Box>

            <Button
              endIcon={<FolderOpenRoundedIcon />}
              onClick={() => onOpen(dependency.key)}
              sx={{
                ...compactButtonSx,
                alignSelf: { md: "center", xs: "start" },
                px: 2,
              }}
              variant="contained"
            >
              開く
            </Button>
          </Box>
        ))}
      </Stack>
    </Paper>
  );
}

function RecommendationPanel({ dependency }) {
  const unresolved = Math.max(dependency.total - dependency.fixable, 0);

  return (
    <Paper elevation={0} sx={{ ...surfaceSx, overflow: "hidden" }}>
      <Grid container spacing={0}>
        <Grid size={{ lg: 8, xs: 12 }}>
          <Box sx={{ px: { sm: 2.5, xs: 2 }, py: 2 }}>
            <Typography sx={{ color: slate[950], fontSize: 14, fontWeight: 800 }}>
              推奨対応
            </Typography>
            <Typography
              component="h3"
              sx={{
                color: slate[950],
                fontSize: { md: 22, xs: 20 },
                fontWeight: 900,
                letterSpacing: 0,
                lineHeight: 1.35,
                mt: 0.5,
              }}
            >
              {dependency.recommendTitle}
            </Typography>
            <Typography sx={{ color: slate[600], fontSize: 14, lineHeight: 1.7, mt: 0.5 }}>
              {dependency.recommendDescription}
            </Typography>
            <Typography sx={{ color: slate[800], fontSize: 14, fontWeight: 700, mt: 1 }}>
              現行バージョン {dependency.version} / 修正バージョン {dependency.fixed} / 検出箇所{" "}
              {dependency.occurrenceCount}件
            </Typography>
          </Box>
        </Grid>

        <Grid
          size={{ lg: 4, xs: 12 }}
          sx={{
            borderLeft: { lg: `1px solid ${slate[200]}`, xs: 0 },
            borderTop: { lg: 0, xs: `1px solid ${slate[200]}` },
          }}
        >
          <Box sx={{ px: { sm: 2.5, xs: 2 }, py: 2 }}>
            <Typography sx={{ color: slate[700], fontSize: 14, fontWeight: 800, mb: 1 }}>
              脆弱性の内訳
            </Typography>
            <Grid container spacing={1.25}>
              <Grid size={6}>
                <BreakdownBox label="修正版あり" tone="emerald" value={dependency.fixable} />
              </Grid>
              <Grid size={6}>
                <BreakdownBox label="確認が必要" tone="amber" value={unresolved} />
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
}

function BreakdownBox({ label, tone, value }) {
  const colors = toneColor(tone);

  return (
    <Box
      sx={{
        bgcolor: "white",
        border: `1px solid ${colors.border}`,
        borderRadius: 2,
        minWidth: 0,
        px: 1.5,
        py: 1.25,
        textAlign: "center",
      }}
    >
      <Typography sx={{ color: colors.fg, fontSize: 12, fontWeight: 800 }}>{label}</Typography>
      <Typography sx={{ color: slate[950], fontSize: 20, fontWeight: 900, mt: 0.5 }}>
        {value}件
      </Typography>
    </Box>
  );
}

function DetailHeader({ dependency }) {
  return (
    <Paper elevation={0} sx={{ ...surfaceSx, p: { sm: 2.5, xs: 2 } }}>
      <Stack direction={{ lg: "row", xs: "column" }} gap={2} justifyContent="space-between">
        <Box sx={{ minWidth: 0 }}>
          <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mb: 1 }}>
            <ToneChip label={dependency.ecosystem} tone="blue" />
            <PackageTypeChip type={dependency.type} />
          </Stack>
          <Typography
            component="h2"
            sx={{
              color: slate[950],
              fontSize: { md: 32, xs: 24 },
              fontWeight: 900,
              letterSpacing: 0,
              lineHeight: 1.2,
              overflowWrap: "anywhere",
            }}
          >
            {dependency.name}
          </Typography>
          <Typography sx={{ color: slate[500], fontSize: 14, mt: 0.75 }}>
            現行バージョン:{" "}
            <Box
              component="span"
              sx={{ color: slate[700], fontFamily: "monospace", fontWeight: 800 }}
            >
              {dependency.version}
            </Box>
          </Typography>
        </Box>

        <Grid container spacing={1} sx={{ minWidth: { lg: 620, xs: 0 } }}>
          <Grid size={{ sm: 3, xs: 6 }}>
            <SmallMetric label="SSVC（最大）">
              <ToneChip label={dependency.ssvcDecision} tone={dependency.ssvcTone} />
            </SmallMetric>
          </Grid>
          <Grid size={{ sm: 3, xs: 6 }}>
            <SmallMetric label="Safety Impact">
              <Typography sx={{ color: slate[900], fontSize: 14, fontWeight: 900 }}>
                {dependency.safetyImpact}
              </Typography>
            </SmallMetric>
          </Grid>
          <Grid size={{ sm: 3, xs: 6 }}>
            <SmallMetric label="修正版あり">
              <Typography sx={{ color: slate[900], fontSize: 14, fontWeight: 900 }}>
                {dependency.fixable} / {dependency.total}件
              </Typography>
            </SmallMetric>
          </Grid>
          <Grid size={{ sm: 3, xs: 6 }}>
            <SmallMetric label="検出箇所数">
              <Typography sx={{ color: slate[900], fontSize: 14, fontWeight: 900 }}>
                {dependency.occurrenceCount}件
              </Typography>
            </SmallMetric>
          </Grid>
        </Grid>
      </Stack>
    </Paper>
  );
}

function TabPanel({ children, id, labelledBy, value }) {
  return (
    <Box
      aria-labelledby={labelledBy}
      hidden={value !== id}
      id={`tab-panel-${id}`}
      role="tabpanel"
      sx={{ display: value === id ? "block" : "none" }}
    >
      {value === id && children}
    </Box>
  );
}

function VulnerabilityTables({ dependency, rows }) {
  const fixableRows = rows.filter((row) => row.status === "fixable");
  const investigateRows = rows.filter((row) => row.status === "investigate");
  const investigationText = dependency.fixable > 0 ? "影響有無を確認" : dependency.recommendAction;

  return (
    <Stack spacing={2}>
      <Stack direction="row" flexWrap="wrap" gap={1}>
        <SummaryPill label="脆弱性" value={rows.length} />
        <SummaryPill label="修正版あり" tone="emerald" value={fixableRows.length} />
        <SummaryPill label="確認が必要" tone="amber" value={investigateRows.length} />
      </Stack>

      <Box sx={{ display: { sm: "block", xs: "none" } }}>
        <Stack spacing={2}>
          <VulnerabilityTable
            rows={fixableRows}
            title="修正版あり"
            tone="emerald"
            valueHeader="修正バージョン"
            valueFor={(row) => row.fixedVersion}
          />
          <VulnerabilityTable
            rows={investigateRows}
            title="確認が必要"
            tone="amber"
            valueHeader="確認内容"
            valueFor={() => investigationText}
          />
        </Stack>
      </Box>

      <Box sx={{ display: { sm: "none", xs: "block" } }}>
        <Stack spacing={1.5}>
          <MobileVulnerabilityGroup
            dependency={dependency}
            rows={fixableRows}
            title="修正版あり"
            tone="emerald"
            valueLabel="修正バージョン"
            valueFor={(row) => row.fixedVersion}
          />
          <MobileVulnerabilityGroup
            dependency={dependency}
            rows={investigateRows}
            title="確認が必要"
            tone="amber"
            valueLabel="確認内容"
            valueFor={() => investigationText}
          />
        </Stack>
      </Box>
    </Stack>
  );
}

function VulnerabilityTable({ rows, title, tone, valueFor, valueHeader }) {
  const colors = toneColor(tone);

  if (!rows.length) {
    return null;
  }

  return (
    <Box
      component="section"
      sx={{
        border: `1px solid ${slate[200]}`,
        borderRadius: 2,
        overflow: "hidden",
      }}
    >
      <Box
        sx={{
          alignItems: "center",
          borderBottom: `1px solid ${slate[200]}`,
          display: "flex",
          justifyContent: "space-between",
          px: 2,
          py: 1.5,
        }}
      >
        <Typography sx={{ color: slate[950], fontSize: 14, fontWeight: 900 }}>
          <Box component="span" sx={{ color: colors.fg }}>
            {title}
          </Box>{" "}
          <Box component="span" sx={{ color: slate[500] }}>
            {rows.length}件
          </Box>
        </Typography>
      </Box>

      <TableContainer sx={{ maxHeight: 360 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell
                sx={{ bgcolor: slate[50], color: slate[500], fontSize: 12, fontWeight: 800 }}
              >
                ID
              </TableCell>
              <TableCell
                sx={{ bgcolor: slate[50], color: slate[500], fontSize: 12, fontWeight: 800 }}
              >
                SSVC判断
              </TableCell>
              <TableCell
                sx={{ bgcolor: slate[50], color: slate[500], fontSize: 12, fontWeight: 800 }}
              >
                {valueHeader}
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow hover key={row.id}>
                <TableCell sx={{ color: slate[950], fontFamily: "monospace", fontWeight: 800 }}>
                  {row.id}
                </TableCell>
                <TableCell sx={{ color: toneColor(row.ssvcTone).fg, fontWeight: 900 }}>
                  {row.ssvcDecision}
                </TableCell>
                <TableCell sx={{ color: slate[950], fontWeight: 700 }}>{valueFor(row)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

function MobileVulnerabilityGroup({ dependency, rows, title, tone, valueFor, valueLabel }) {
  const colors = toneColor(tone);

  if (!rows.length) {
    return null;
  }

  return (
    <Box
      component="section"
      sx={{
        border: `1px solid ${slate[200]}`,
        borderRadius: 2,
        p: 1.5,
      }}
    >
      <Typography sx={{ color: slate[950], fontSize: 14, fontWeight: 900, px: 0.5 }}>
        <Box component="span" sx={{ color: colors.fg }}>
          {title}
        </Box>{" "}
        <Box component="span" sx={{ color: slate[500] }}>
          {rows.length}件
        </Box>
      </Typography>

      <Stack spacing={1.5} sx={{ mt: 1.5 }}>
        {rows.map((row) => (
          <Box
            component="article"
            key={row.id}
            sx={{
              border: `1px solid ${slate[200]}`,
              borderRadius: 2,
              p: 2,
            }}
          >
            <Stack direction="row" gap={1} justifyContent="space-between">
              <Typography
                sx={{
                  color: slate[950],
                  fontFamily: "monospace",
                  fontSize: 12,
                  fontWeight: 900,
                  overflowWrap: "anywhere",
                }}
              >
                {row.id}
              </Typography>
              <Typography
                sx={{
                  color: toneColor(row.ssvcTone).fg,
                  flexShrink: 0,
                  fontSize: 12,
                  fontWeight: 900,
                }}
              >
                {row.ssvcDecision}
              </Typography>
            </Stack>

            <Typography
              sx={{ color: slate[950], fontSize: 14, fontWeight: 900, lineHeight: 1.6, mt: 1.5 }}
            >
              {dependency.name} {dependency.version}
            </Typography>
            <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700, mt: 0.5 }}>
              {dependency.ecosystem} / {dependency.occurrenceCount}箇所で検出
            </Typography>

            <Grid
              container
              sx={{
                borderTop: `1px solid ${slate[200]}`,
                mt: 1.75,
                pt: 1.5,
                textAlign: "center",
              }}
            >
              <Grid size={6} sx={{ borderRight: `1px solid ${slate[200]}`, px: 1 }}>
                <Typography sx={{ color: slate[500], fontSize: 11, fontWeight: 800 }}>
                  SSVC
                </Typography>
                <Typography
                  sx={{ color: toneColor(row.ssvcTone).fg, fontSize: 12, fontWeight: 900, mt: 0.5 }}
                >
                  {row.ssvcDecision}
                </Typography>
              </Grid>
              <Grid size={6} sx={{ px: 1 }}>
                <Typography sx={{ color: slate[500], fontSize: 11, fontWeight: 800 }}>
                  {valueLabel}
                </Typography>
                <Typography
                  sx={{
                    color: slate[950],
                    fontSize: 12,
                    fontWeight: 900,
                    mt: 0.5,
                    overflowWrap: "anywhere",
                  }}
                >
                  {valueFor(row)}
                </Typography>
              </Grid>
            </Grid>
          </Box>
        ))}
      </Stack>
    </Box>
  );
}

function DependencyPaths({ dependency }) {
  return (
    <Box
      sx={{
        bgcolor: slate[50],
        border: `1px solid ${slate[200]}`,
        borderRadius: 2,
        p: { sm: 2.5, xs: 2 },
      }}
    >
      <Typography component="h3" sx={{ color: slate[900], fontWeight: 800, mb: 1.5 }}>
        検出箇所と依存経路
      </Typography>
      <Stack spacing={1.5} sx={{ maxHeight: 560, overflow: "auto", pr: 0.5 }}>
        {dependency.occurrences.map((occurrence, index) => (
          <Box
            key={occurrence.occurrenceId}
            sx={{
              bgcolor: "white",
              border: `1px solid ${slate[200]}`,
              borderRadius: 2,
              p: 2,
            }}
          >
            <Stack direction="row" flexWrap="wrap" gap={1} sx={{ alignItems: "center", mb: 1 }}>
              <Chip
                label={index + 1}
                size="small"
                sx={{
                  bgcolor: slate[100],
                  borderRadius: 999,
                  color: slate[600],
                  fontSize: 12,
                  fontWeight: 900,
                  height: 24,
                }}
              />
              <Typography sx={{ color: slate[900], fontSize: 14, fontWeight: 800 }}>
                {occurrence.location}
              </Typography>
              <PackageTypeChip type={occurrence.type} />
            </Stack>
            <Box
              sx={{
                bgcolor: slate[50],
                borderRadius: 2,
                color: slate[700],
                fontFamily: "monospace",
                fontSize: 14,
                lineHeight: 1.8,
                overflow: "auto",
                p: 1.5,
                whiteSpace: "pre",
              }}
            >
              {occurrence.path}
            </Box>
          </Box>
        ))}
      </Stack>
    </Box>
  );
}

function TodoList({ dependency }) {
  return (
    <Box
      sx={{
        border: `1px solid ${slate[200]}`,
        borderRadius: 2,
        p: 2,
      }}
    >
      <Stack direction="row" gap={1} sx={{ alignItems: "center", mb: 1.25 }}>
        <CheckCircleRoundedIcon sx={{ color: toneColors.emerald.fg, fontSize: 20 }} />
        <Typography sx={{ color: slate[900], fontSize: 14, fontWeight: 900 }}>
          対応タスク
        </Typography>
      </Stack>
      <Stack spacing={1}>
        {dependency.todos.map((todo, index) => (
          <Stack direction="row" gap={1} key={todo} sx={{ alignItems: "flex-start" }}>
            <Box
              component="span"
              sx={{
                bgcolor: slate[100],
                borderRadius: 999,
                color: slate[600],
                flex: "0 0 auto",
                fontSize: 11,
                fontWeight: 900,
                lineHeight: "20px",
                textAlign: "center",
                width: 20,
              }}
            >
              {index + 1}
            </Box>
            <Typography sx={{ color: slate[700], fontSize: 13, lineHeight: 1.6 }}>
              {todo}
            </Typography>
          </Stack>
        ))}
      </Stack>
    </Box>
  );
}

function DecisionContext({ dependency }) {
  const factorItems = [
    ["Exploitation", dependency.ssvcFactors.exploitation],
    ["System Exposure", dependency.ssvcFactors.systemExposure],
    ["Automatable", dependency.ssvcFactors.automatable],
    ["Human Impact", dependency.ssvcFactors.humanImpact],
  ];

  return (
    <Box
      sx={{
        border: `1px solid ${slate[200]}`,
        borderRadius: 2,
        p: 2,
      }}
    >
      <Stack direction="row" gap={1} sx={{ alignItems: "center", mb: 1 }}>
        <ManageSearchRoundedIcon sx={{ color: toneColor(dependency.ssvcTone).fg, fontSize: 20 }} />
        <Typography sx={{ color: slate[900], fontSize: 14, fontWeight: 900 }}>
          SSVC判断メモ
        </Typography>
      </Stack>
      <Typography sx={{ color: slate[600], fontSize: 13, lineHeight: 1.7 }}>
        {dependency.ssvcReason}
      </Typography>
      <Grid container spacing={1} sx={{ mt: 1.5 }}>
        {factorItems.map(([label, value]) => (
          <Grid key={label} size={{ md: 6, xs: 12 }}>
            <Box sx={{ bgcolor: slate[50], borderRadius: 2, px: 1.5, py: 1 }}>
              <Typography sx={{ color: slate[500], fontSize: 11, fontWeight: 800 }}>
                {label}
              </Typography>
              <Typography sx={{ color: slate[900], fontSize: 13, fontWeight: 900, mt: 0.25 }}>
                {value}
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

function DetailView({ dependency, onBack, tab, onTabChange }) {
  const rows = useMemo(() => buildVulns(dependency), [dependency]);
  const fixableRows = rows.filter((row) => row.status === "fixable");
  const investigateRows = rows.filter((row) => row.status === "investigate");
  const completion = dependency.total
    ? Math.round((dependency.fixable / dependency.total) * 100)
    : 0;

  return (
    <Stack spacing={2}>
      <Box>
        <Button
          onClick={onBack}
          startIcon={<ArrowBackRoundedIcon />}
          sx={{
            ...compactButtonSx,
            bgcolor: "white",
            borderColor: slate[200],
            color: slate[700],
            "&:hover": {
              bgcolor: slate[50],
              borderColor: slate[300],
            },
          }}
          variant="outlined"
        >
          一覧へ
        </Button>
      </Box>

      <DetailHeader dependency={dependency} />
      <RecommendationPanel dependency={dependency} />

      <Grid container spacing={2}>
        <Grid size={{ lg: 8, xs: 12 }}>
          <Paper elevation={0} sx={{ ...surfaceSx, overflow: "hidden" }}>
            <Box sx={{ borderBottom: `1px solid ${slate[200]}`, px: 2, pt: 1 }}>
              <Tabs
                aria-label="依存コンポーネント詳細"
                onChange={(_event, value) => onTabChange(value)}
                scrollButtons="auto"
                sx={{
                  minHeight: 48,
                  "& .MuiTabs-indicator": { backgroundColor: slate[950] },
                  "& .MuiTab-root": {
                    borderTopLeftRadius: 2,
                    borderTopRightRadius: 2,
                    fontSize: 14,
                    fontWeight: 800,
                    letterSpacing: 0,
                    minHeight: 48,
                    textTransform: "none",
                  },
                  "& .Mui-selected": {
                    bgcolor: slate[950],
                    color: "white !important",
                  },
                }}
                value={tab}
                variant="scrollable"
              >
                <Tab
                  icon={<BugReportRoundedIcon />}
                  iconPosition="start"
                  id="tab-vulns"
                  label={`脆弱性一覧 ${rows.length}`}
                  value="vulns"
                  wrapped
                  aria-controls="tab-panel-vulns"
                />
                <Tab
                  icon={<RouteRoundedIcon />}
                  iconPosition="start"
                  id="tab-path"
                  label={`検出箇所・依存経路 ${dependency.occurrenceCount}`}
                  value="path"
                  wrapped
                  aria-controls="tab-panel-path"
                />
              </Tabs>
            </Box>

            <Box sx={{ p: { sm: 2.5, xs: 2 } }}>
              <TabPanel id="vulns" labelledBy="tab-vulns" value={tab}>
                <VulnerabilityTables dependency={dependency} rows={rows} />
              </TabPanel>
              <TabPanel id="path" labelledBy="tab-path" value={tab}>
                <DependencyPaths dependency={dependency} />
              </TabPanel>
            </Box>
          </Paper>
        </Grid>

        <Grid size={{ lg: 4, xs: 12 }}>
          <Stack spacing={2}>
            <Paper elevation={0} sx={{ ...surfaceSx, p: 2 }}>
              <Typography sx={{ color: slate[900], fontSize: 14, fontWeight: 900, mb: 1 }}>
                解消見込み
              </Typography>
              <Stack direction="row" gap={1} sx={{ alignItems: "center", mb: 1 }}>
                <Typography sx={{ color: slate[950], fontSize: 28, fontWeight: 900 }}>
                  {completion}%
                </Typography>
                <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
                  {dependency.fixable} / {dependency.total}件
                </Typography>
              </Stack>
              <LinearProgress
                value={completion}
                variant="determinate"
                sx={{
                  bgcolor: slate[100],
                  borderRadius: 999,
                  height: 8,
                  "& .MuiLinearProgress-bar": {
                    bgcolor: dependency.fixable > 0 ? toneColors.emerald.fg : toneColors.amber.fg,
                    borderRadius: 999,
                  },
                }}
              />
              <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mt: 1.5 }}>
                <SummaryPill label="修正版あり" tone="emerald" value={fixableRows.length} />
                <SummaryPill label="確認が必要" tone="amber" value={investigateRows.length} />
              </Stack>
            </Paper>
            <DecisionContext dependency={dependency} />
            <TodoList dependency={dependency} />
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  );
}

function SBOMDependencyRemediationPreview({
  initialDependencyKey,
  initialView = "list",
  showSideContext = true,
}) {
  const dependencies = useMemo(() => groupSbomEntries(sbomEntries), []);
  const fallbackKey = dependencies[0]?.key;
  const [selectedKey, setSelectedKey] = useState(initialDependencyKey ?? fallbackKey);
  const [view, setView] = useState(initialView);
  const [tab, setTab] = useState("vulns");
  const selectedDependency =
    dependencies.find((dependency) => dependency.key === selectedKey) ?? dependencies[0];

  const openDetail = (dependencyKeyValue) => {
    setSelectedKey(dependencyKeyValue);
    setTab("vulns");
    setView("detail");
  };

  return (
    <Box sx={rootSx}>
      <Stack spacing={2} sx={pageSx}>
        {showSideContext && (
          <Box
            sx={{
              alignItems: { md: "center", xs: "flex-start" },
              display: "flex",
              flexDirection: { md: "row", xs: "column" },
              gap: 1.5,
              justifyContent: "space-between",
            }}
          >
            <Box sx={{ minWidth: 0 }}>
              <Typography
                component="h1"
                sx={{
                  color: slate[950],
                  fontSize: { md: 26, xs: 22 },
                  fontWeight: 900,
                  letterSpacing: 0,
                  lineHeight: 1.2,
                }}
              >
                SBOM Dependency Remediation Preview
              </Typography>
              <Typography sx={{ color: slate[500], fontSize: 13, fontWeight: 700, mt: 0.75 }}>
                依存コンポーネント単位で、SSVC優先度・修正版有無・検出箇所を確認できます。
              </Typography>
            </Box>
            <Stack direction="row" flexWrap="wrap" gap={1}>
              <ToneChip label={`${dependencies.length} components`} tone="blue" />
              <ToneChip label={`${sbomEntries.length} occurrences`} tone="emerald" />
            </Stack>
          </Box>
        )}

        {view === "list" ? (
          <ListView dependencies={dependencies} onOpen={openDetail} />
        ) : (
          <DetailView
            dependency={selectedDependency}
            onBack={() => setView("list")}
            onTabChange={setTab}
            tab={tab}
          />
        )}
      </Stack>
    </Box>
  );
}

const meta = {
  component: SBOMDependencyRemediationPreview,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
  title: "Status/SBOM Dependency Remediation Preview",
};

export default meta;

export const Default = {
  args: {
    initialView: "list",
  },
};

export const Detail = {
  args: {
    initialDependencyKey: "npm::lodash::4.17.20",
    initialView: "detail",
  },
};
