/* eslint-disable @cspell/spellchecker, react/prop-types */
import {
  Box,
  Button,
  Chip,
  Divider,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

if (!import.meta.env.VITE_AUTH_SERVICE) {
  import.meta.env.VITE_AUTH_SERVICE = "firebase";
}

const sbomEntries = [
  {
    occurrenceId: "web-lodash",
    project: "web-app",
    name: "lodash",
    ecosystem: "npm",
    version: "4.17.20",
    bomRef: "pkg:npm/lodash@4.17.20#web-app",
    type: "直接依存",
    location: "web-app / package.json",
    safetyImpact: "negligible",
    total: 24,
    ssvcDecision: "Immediate",
    ssvcTone: "rose",
    ssvcReason:
      "公開PoCがあり、本番系での露出と自動化可能性を考慮して、通常サイクルを待たずに対応します。",
    ssvcFactors: {
      exploitation: "Public PoC",
      systemExposure: "Open",
      automatable: "Yes",
      humanImpact: "Medium",
    },
    fixed: "4.17.21+",
    fixable: 18,
    investigate: 4,
    notAffected: 2,
    responseLabel: "修正版あり",
    responseTone: "emerald",
    recommendAction: "4.17.21以上へ更新",
    recommendTitle: "4.17.21以上へ更新してください",
    recommendDescription: "この更新で 18 / 24件 の脆弱性を解消できます。",
    todos: [
      "package.json の lodash を 4.17.21 以上に更新",
      "lockfileを再生成",
      "単体テスト・依存テストを実行",
      "PRを作成してレビュー依頼",
    ],
    pathHtml: "web-app<br>└─ lodash 4.17.20",
  },
  {
    occurrenceId: "worker-lodash",
    project: "worker",
    name: "lodash",
    ecosystem: "npm",
    version: "4.17.20",
    bomRef: "pkg:npm/lodash@4.17.20#worker",
    type: "直接依存",
    location: "worker / package.json",
    safetyImpact: "negligible",
    total: 24,
    ssvcDecision: "Immediate",
    ssvcTone: "rose",
    ssvcReason:
      "公開PoCがあり、本番系での露出と自動化可能性を考慮して、通常サイクルを待たずに対応します。",
    ssvcFactors: {
      exploitation: "Public PoC",
      systemExposure: "Open",
      automatable: "Yes",
      humanImpact: "Medium",
    },
    fixed: "4.17.21+",
    fixable: 18,
    investigate: 4,
    notAffected: 2,
    responseLabel: "修正版あり",
    responseTone: "emerald",
    recommendAction: "4.17.21以上へ更新",
    recommendTitle: "4.17.21以上へ更新してください",
    recommendDescription: "この更新で 18 / 24件 の脆弱性を解消できます。",
    todos: [
      "package.json の lodash を 4.17.21 以上に更新",
      "lockfileを再生成",
      "単体テスト・依存テストを実行",
      "PRを作成してレビュー依頼",
    ],
    pathHtml: "worker<br>└─ lodash 4.17.20",
  },
  {
    occurrenceId: "api-spring-core",
    project: "api-service",
    name: "spring-core",
    ecosystem: "Maven",
    version: "5.3.18",
    bomRef: "pkg:maven/org.springframework/spring-core@5.3.18#api-service",
    type: "推移的依存",
    location: "api-service / pom.xml",
    safetyImpact: "moderate",
    total: 64,
    ssvcDecision: "Out-of-Cycle",
    ssvcTone: "amber",
    ssvcReason:
      "公開PoCがあり、推移的依存として本番影響が残るため、通常メンテナンスより前倒しで親コンポーネント更新を進めます。",
    ssvcFactors: {
      exploitation: "Public PoC",
      systemExposure: "Controlled",
      automatable: "No",
      humanImpact: "Medium",
    },
    fixed: "5.3.33+",
    fixable: 48,
    investigate: 10,
    notAffected: 6,
    responseLabel: "親更新で対応",
    responseTone: "emerald",
    recommendAction: "spring-boot-starter-web更新",
    recommendTitle: "親コンポーネントを更新してください",
    recommendDescription: "spring-boot-starter-webを更新すると 48 / 64件 の脆弱性を解消できます。",
    todos: [
      "spring-boot-starter-web の更新可能バージョンを確認",
      "依存解決後の spring-core バージョンを確認",
      "統合テストを実行",
      "残る脆弱性はVEX判断または例外登録",
    ],
    pathHtml:
      "api-service<br>└─ spring-boot-starter-web 2.6.6<br>&nbsp;&nbsp;&nbsp;└─ spring-core 5.3.18",
  },
  {
    occurrenceId: "batch-spring-core",
    project: "batch-service",
    name: "spring-core",
    ecosystem: "Maven",
    version: "5.3.18",
    bomRef: "pkg:maven/org.springframework/spring-core@5.3.18#batch-service",
    type: "推移的依存",
    location: "batch-service / pom.xml",
    safetyImpact: "moderate",
    total: 64,
    ssvcDecision: "Out-of-Cycle",
    ssvcTone: "amber",
    ssvcReason:
      "公開PoCがあり、推移的依存として本番影響が残るため、通常メンテナンスより前倒しで親コンポーネント更新を進めます。",
    ssvcFactors: {
      exploitation: "Public PoC",
      systemExposure: "Controlled",
      automatable: "No",
      humanImpact: "Medium",
    },
    fixed: "5.3.33+",
    fixable: 48,
    investigate: 10,
    notAffected: 6,
    responseLabel: "親更新で対応",
    responseTone: "emerald",
    recommendAction: "spring-boot-starter-web更新",
    recommendTitle: "親コンポーネントを更新してください",
    recommendDescription: "spring-boot-starter-webを更新すると 48 / 64件 の脆弱性を解消できます。",
    todos: [
      "spring-boot-starter-web の更新可能バージョンを確認",
      "依存解決後の spring-core バージョンを確認",
      "統合テストを実行",
      "残る脆弱性はVEX判断または例外登録",
    ],
    pathHtml:
      "batch-service<br>└─ spring-batch-core 4.3.6<br>&nbsp;&nbsp;&nbsp;└─ spring-core 5.3.18",
  },
  {
    occurrenceId: "runtime-openssl",
    project: "api-runtime",
    name: "openssl",
    ecosystem: "Debian",
    version: "1.1.1n",
    bomRef: "pkg:deb/debian/openssl@1.1.1n#api-runtime",
    type: "OS package",
    location: "api-runtime / Docker image",
    safetyImpact: "low",
    total: 11,
    ssvcDecision: "Scheduled",
    ssvcTone: "blue",
    ssvcReason:
      "悪用確認はなく、OSパッケージ由来でベースイメージ更新の確認が必要なため、定期メンテナンス枠で扱います。",
    ssvcFactors: {
      exploitation: "None",
      systemExposure: "Controlled",
      automatable: "No",
      humanImpact: "Low",
    },
    fixed: "ベースイメージ更新",
    fixable: 0,
    investigate: 11,
    notAffected: 0,
    responseLabel: "確認が必要",
    responseTone: "amber",
    recommendAction: "ベースイメージ更新を確認",
    recommendTitle: "ベースイメージ更新を確認してください",
    recommendDescription:
      "コンテナイメージ由来のため、パッケージ単体ではなくベースイメージの更新で確認します。",
    todos: [
      "DockerfileのFROMイメージを確認",
      "新しいベースイメージでSBOMを再生成",
      "ランタイム互換性を確認",
      "残る脆弱性をディストリビューションの修正状況で確認",
    ],
    pathHtml: "api-runtime image<br>└─ debian:bullseye<br>&nbsp;&nbsp;&nbsp;└─ openssl 1.1.1n",
  },
  {
    occurrenceId: "admin-ansi-regex",
    project: "admin",
    name: "ansi-regex",
    ecosystem: "npm",
    version: "3.0.0",
    bomRef: "pkg:npm/ansi-regex@3.0.0#admin",
    type: "推移的依存",
    location: "admin / package-lock.json",
    safetyImpact: "negligible",
    total: 7,
    ssvcDecision: "Defer",
    ssvcTone: "slate",
    ssvcReason: "開発時のみの依存で本番到達性が低いため、期限付きの例外として継続監視します。",
    ssvcFactors: {
      exploitation: "None",
      systemExposure: "Small",
      automatable: "No",
      humanImpact: "Low",
    },
    fixed: "例外期限 2026-09-30",
    fixable: 0,
    investigate: 2,
    notAffected: 5,
    responseLabel: "期限付き例外",
    responseTone: "slate",
    recommendAction: "延期理由を記録",
    recommendTitle: "延期理由と再評価期限を記録してください",
    recommendDescription:
      "本番利用条件では影響が低いため、利用経路と再評価期限を残して監視します。",
    todos: [
      "依存経路が開発時のみであることを確認",
      "VEXまたは例外理由を記録",
      "再評価期限を設定",
      "親ツール更新時に再確認",
    ],
    pathHtml: "admin<br>└─ eslint 6.8.0<br>&nbsp;&nbsp;&nbsp;└─ ansi-regex 3.0.0",
  },
];

const ssvcDecisionConfig = {
  Immediate: { rank: 1 },
  "Out-of-Cycle": { rank: 2 },
  Scheduled: { rank: 3 },
  Defer: { rank: 4 },
};

const slate = {
  50: "#f8fafc",
  100: "#f1f5f9",
  200: "#e2e8f0",
  300: "#cbd5e1",
  500: "#64748b",
  600: "#475569",
  700: "#334155",
  800: "#1e293b",
  900: "#0f172a",
  950: "#020617",
};

const tones = {
  amber: { background: "#fef3c7", border: "#fcd34d", color: "#b45309" },
  blue: { background: "#dbeafe", border: "#bfdbfe", color: "#1d4ed8" },
  emerald: { background: "#d1fae5", border: "#a7f3d0", color: "#047857" },
  indigo: { background: "#e0e7ff", border: "#c7d2fe", color: "#4338ca" },
  rose: { background: "#ffe4e6", border: "#fecdd3", color: "#be123c" },
  slate: { background: slate[100], border: slate[200], color: slate[700] },
};

const shellSx = {
  bgcolor: slate[50],
  color: slate[900],
  minHeight: "100vh",
  px: { lg: 4, sm: 2.5, xs: 2 },
  py: { sm: 3, xs: 2 },
};

const pageSx = {
  maxWidth: 1500,
  mx: "auto",
};

const softSurfaceSx = {
  bgcolor: "white",
  border: `1px solid ${slate[200]}`,
  boxShadow: "0 18px 45px rgba(15, 23, 42, 0.08)",
};

const buttonSx = {
  borderRadius: 1.5,
  fontSize: 14,
  fontWeight: 700,
  minHeight: 40,
  px: 2,
  textTransform: "none",
};

const compactText = {
  fontSize: 14,
  letterSpacing: 0,
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

function tone(toneName) {
  return tones[toneName] ?? tones.slate;
}

function StatusChip({ label, toneName = "slate" }) {
  const colors = tone(toneName);

  return (
    <Chip
      label={label}
      size="small"
      sx={{
        bgcolor: colors.background,
        borderRadius: 999,
        color: colors.color,
        fontSize: 12,
        fontWeight: 800,
        height: 26,
        letterSpacing: 0,
        px: 0.25,
      }}
    />
  );
}

function OsPackageChip({ type }) {
  if (!isOsPackage(type)) return null;
  return <StatusChip label="OSパッケージ" toneName="blue" />;
}

function dependencyProgressLabel(dependency) {
  return (
    {
      Immediate: "未着手",
      "Out-of-Cycle": "対応中",
      Scheduled: "調査中",
      Defer: "延期",
    }[dependency.ssvcDecision] ?? "確認中"
  );
}

function dependencyProgressTone(dependency) {
  return (
    {
      Immediate: "slate",
      "Out-of-Cycle": "blue",
      Scheduled: "amber",
      Defer: "slate",
    }[dependency.ssvcDecision] ?? "slate"
  );
}

function ListView({ dependencies, onOpen }) {
  return (
    <Paper elevation={0} sx={{ ...softSurfaceSx, borderRadius: 1, overflow: "hidden" }}>
      <Box
        sx={{
          bgcolor: slate[50],
          borderBottom: `1px solid ${slate[200]}`,
          color: slate[500],
          display: { md: "grid", xs: "none" },
          fontSize: 12,
          fontWeight: 800,
          gap: 1.5,
          gridTemplateColumns: "minmax(0, 1.5fr) minmax(0, 1fr) minmax(0, 1fr) auto",
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
                md: "minmax(0, 1.5fr) minmax(0, 1fr) minmax(0, 1fr) auto",
                xs: "1fr",
              },
              p: 2,
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
                    lineHeight: 1.4,
                    minWidth: 0,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {dependency.name}
                </Typography>
                <OsPackageChip type={dependency.type} />
              </Stack>
              <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700, mt: 0.5 }}>
                {dependency.ecosystem} /{" "}
                <Box component="span" sx={{ fontFamily: "monospace" }}>
                  {dependency.version}
                </Box>{" "}
                / {dependency.occurrenceCount}箇所
              </Typography>
            </Box>

            <Box sx={{ alignItems: "center", display: "flex" }}>
              <StatusChip label={dependency.ssvcDecision} toneName={dependency.ssvcTone} />
            </Box>

            <Box sx={{ alignItems: "center", display: "flex" }}>
              <StatusChip
                label={dependencyProgressLabel(dependency)}
                toneName={dependencyProgressTone(dependency)}
              />
            </Box>

            <Button
              onClick={() => onOpen(dependency.key)}
              sx={{
                ...buttonSx,
                alignSelf: { md: "center", xs: "start" },
                bgcolor: "#4f46e5",
                borderRadius: 1,
                color: "white",
                fontWeight: 800,
                minHeight: 36,
                px: 1.5,
                "&:hover": { bgcolor: "#4338ca" },
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

function DetailSummary({ dependency }) {
  return (
    <Paper
      elevation={0}
      sx={{ ...softSurfaceSx, borderRadius: 2, mb: { sm: 2.5, xs: 2 }, p: { sm: 2.5, xs: 2 } }}
    >
      <Stack direction={{ lg: "row", xs: "column" }} gap={2} justifyContent="space-between">
        <Box sx={{ minWidth: 0 }}>
          <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mb: 1 }}>
            <StatusChip label={dependency.ecosystem} toneName="indigo" />
            <OsPackageChip type={dependency.type} />
          </Stack>
          <Typography
            component="h2"
            sx={{
              color: slate[950],
              fontSize: { md: 30, xs: 24 },
              fontWeight: 900,
              letterSpacing: 0,
              lineHeight: 1.2,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {dependency.name}
          </Typography>
          <Typography sx={{ color: slate[500], fontSize: 14, mt: 0.75 }}>
            現行バージョン:{" "}
            <Box
              component="span"
              sx={{ color: slate[700], fontFamily: "monospace", fontWeight: 700 }}
            >
              {dependency.version}
            </Box>
          </Typography>
        </Box>

        <Grid container spacing={1} sx={{ minWidth: { lg: 620, xs: 0 } }}>
          <Grid size={{ sm: 3, xs: 6 }}>
            <SummaryBox label="SSVC（最大）">
              <StatusChip label={dependency.ssvcDecision} toneName={dependency.ssvcTone} />
            </SummaryBox>
          </Grid>
          <Grid size={{ sm: 3, xs: 6 }}>
            <SummaryBox label="Safety Impact">{dependency.safetyImpact || "-"}</SummaryBox>
          </Grid>
          <Grid size={{ sm: 3, xs: 6 }}>
            <SummaryBox label="修正版あり">
              {dependency.fixable} / {dependency.total}件
            </SummaryBox>
          </Grid>
          <Grid size={{ sm: 3, xs: 6 }}>
            <SummaryBox label="検出箇所数">{dependency.occurrenceCount}件</SummaryBox>
          </Grid>
        </Grid>
      </Stack>
    </Paper>
  );
}

function SummaryBox({ children, label }) {
  return (
    <Box
      sx={{
        bgcolor: slate[50],
        borderRadius: 1.5,
        minWidth: 0,
        px: 1.5,
        py: 1.5,
        textAlign: "center",
      }}
    >
      <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>{label}</Typography>
      <Box
        sx={{
          color: slate[900],
          fontSize: 14,
          fontWeight: 900,
          mt: 0.75,
          overflowWrap: "anywhere",
        }}
      >
        {children}
      </Box>
    </Box>
  );
}

function RecommendationSection({ dependency }) {
  const unresolved = Math.max(dependency.total - dependency.fixable, 0);

  return (
    <Paper elevation={0} sx={{ ...softSurfaceSx, borderRadius: 2, mb: 2.5, overflow: "hidden" }}>
      <Grid container>
        <Grid size={{ lg: 8.8, xs: 12 }}>
          <Box sx={{ alignSelf: "center", px: { sm: 2.5, xs: 2 }, py: 2 }}>
            <Typography sx={{ color: slate[950], fontSize: 14, fontWeight: 800 }}>
              推奨対応
            </Typography>
            <Typography
              component="h3"
              sx={{
                color: slate[950],
                fontSize: 20,
                fontWeight: 900,
                letterSpacing: 0,
                lineHeight: 1.35,
                mt: 0.5,
              }}
            >
              {dependency.recommendTitle}
            </Typography>
            <Typography
              sx={{ color: slate[600], fontSize: 14, lineHeight: 1.6, mt: 0.5, maxWidth: 980 }}
            >
              {dependency.recommendDescription}
            </Typography>
            <Typography sx={{ color: slate[800], fontSize: 14, fontWeight: 700, mt: 1 }}>
              現行バージョン {dependency.version} / 修正バージョン {dependency.fixed} / 検出箇所{" "}
              {dependency.occurrenceCount}件
            </Typography>
          </Box>
        </Grid>
        <Grid
          size={{ lg: 3.2, xs: 12 }}
          sx={{
            borderLeft: { lg: `1px solid ${slate[200]}`, xs: 0 },
            borderTop: { lg: 0, xs: `1px solid ${slate[200]}` },
          }}
        >
          <Box sx={{ px: { sm: 2.5, xs: 2 }, py: 2 }}>
            <Typography sx={{ color: slate[700], fontSize: 14, fontWeight: 800, mb: 1 }}>
              脆弱性の内訳
            </Typography>
            <Grid container spacing={1}>
              <Grid size={6}>
                <BreakdownBox label="修正版あり" toneName="emerald" value={dependency.fixable} />
              </Grid>
              <Grid size={6}>
                <BreakdownBox label="確認が必要" toneName="amber" value={unresolved} />
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
}

function BreakdownBox({ label, toneName, value }) {
  const colors = tone(toneName);

  return (
    <Box
      sx={{
        bgcolor: "white",
        border: `1px solid ${colors.border}`,
        borderRadius: 1,
        minWidth: 0,
        px: 1.5,
        py: 1.5,
        textAlign: "center",
      }}
    >
      <Typography sx={{ color: colors.color, fontSize: 12, fontWeight: 800 }}>{label}</Typography>
      <Typography sx={{ color: slate[950], fontSize: 18, fontWeight: 900, mt: 0.5 }}>
        {value}件
      </Typography>
    </Box>
  );
}

function DetailTabs({ dependency, rows, tab, onTabChange }) {
  return (
    <Paper elevation={0} sx={{ ...softSurfaceSx, borderRadius: 2, overflow: "hidden" }}>
      <Box sx={{ borderBottom: `1px solid ${slate[200]}`, px: 2, pt: 2 }}>
        <Box
          aria-label="依存コンポーネント詳細"
          role="tablist"
          sx={{
            bgcolor: { sm: "transparent", xs: slate[50] },
            borderRadius: { sm: 0, xs: 2 },
            display: "flex",
            gap: 1,
            overflowX: "auto",
            p: { sm: 0, xs: 1 },
          }}
        >
          <TabButton
            count={rows.length}
            id="vulns"
            label="脆弱性一覧"
            onClick={() => onTabChange("vulns")}
            selected={tab === "vulns"}
          />
          <TabButton
            count={dependency.occurrenceCount}
            id="path"
            label="検出箇所・依存経路"
            onClick={() => onTabChange("path")}
            selected={tab === "path"}
          />
        </Box>
      </Box>

      <Box sx={{ p: { sm: 2.5, xs: 2 } }}>
        {tab === "vulns" ? (
          <VulnerabilityPanel dependency={dependency} rows={rows} />
        ) : (
          <DependencyPathPanel dependency={dependency} />
        )}
      </Box>
    </Paper>
  );
}

function TabButton({ count, id, label, onClick, selected }) {
  return (
    <Box
      aria-controls={`tab-${id}`}
      aria-selected={selected}
      component="button"
      id={`tab-button-${id}`}
      onClick={onClick}
      role="tab"
      sx={{
        alignItems: "center",
        bgcolor: selected ? slate[900] : "transparent",
        border: { sm: `1px solid ${selected ? slate[900] : "transparent"}`, xs: 0 },
        borderBottom: 0,
        borderRadius: { sm: "12px 12px 0 0", xs: 999 },
        color: selected ? "white" : slate[600],
        cursor: "pointer",
        display: "inline-flex",
        flex: "0 0 auto",
        font: "inherit",
        fontSize: 14,
        fontWeight: 800,
        gap: 1,
        px: { sm: 2, xs: 1.5 },
        py: { sm: 1.5, xs: 1 },
        transition: "background-color 120ms ease, border-color 120ms ease, color 120ms ease",
        "&:hover": {
          bgcolor: selected ? slate[900] : slate[50],
          color: selected ? "white" : slate[900],
        },
        "&:focus-visible": {
          outline: "2px solid #6366f1",
          outlineOffset: 2,
        },
      }}
      type="button"
    >
      <Box component="span">{label}</Box>
      <Box
        component="span"
        sx={{
          bgcolor: selected ? "rgba(255, 255, 255, 0.18)" : slate[200],
          borderRadius: 999,
          color: selected ? "white" : slate[600],
          fontSize: 12,
          fontWeight: 900,
          lineHeight: 1,
          px: 1,
          py: 0.5,
        }}
      >
        {count}
      </Box>
    </Box>
  );
}

function VulnerabilityPanel({ dependency, rows }) {
  const fixableRows = rows.filter((row) => row.status === "fixable");
  const investigateRows = rows.filter((row) => row.status === "investigate");
  const investigationText = dependency.fixable > 0 ? "影響有無を確認" : dependency.recommendAction;

  return (
    <Stack spacing={2}>
      <Stack direction="row" flexWrap="wrap" gap={1}>
        <SummaryPill label="脆弱性" value={rows.length} />
        <SummaryPill label="修正版あり" toneName="emerald" value={fixableRows.length} />
        <SummaryPill label="確認が必要" toneName="amber" value={investigateRows.length} />
      </Stack>

      <Box sx={{ display: { sm: "block", xs: "none" } }}>
        <Stack spacing={2}>
          <VulnTable
            rows={fixableRows}
            title="修正版あり"
            toneName="emerald"
            valueHeader="修正バージョン"
            valueFor={(row) => row.fixedVersion}
          />
          <VulnTable
            rows={investigateRows}
            title="確認が必要"
            toneName="amber"
            valueHeader="確認内容"
            valueFor={() => investigationText}
          />
        </Stack>
      </Box>

      <Box sx={{ display: { sm: "none", xs: "block" } }}>
        <Stack spacing={1.5}>
          <MobileVulnGroup
            dependency={dependency}
            rows={fixableRows}
            title="修正版あり"
            toneName="emerald"
            valueLabel="修正バージョン"
            valueFor={(row) => row.fixedVersion}
          />
          <MobileVulnGroup
            dependency={dependency}
            rows={investigateRows}
            title="確認が必要"
            toneName="amber"
            valueLabel="確認内容"
            valueFor={() => investigationText}
          />
        </Stack>
      </Box>
    </Stack>
  );
}

function SummaryPill({ label, toneName = "slate", value }) {
  const colors = tone(toneName);

  return (
    <Box
      component="span"
      sx={{
        bgcolor: "white",
        border: `1px solid ${slate[200]}`,
        borderRadius: 999,
        color: slate[950],
        display: "inline-flex",
        fontSize: 12,
        fontWeight: 900,
        lineHeight: 1,
        px: 1.5,
        py: 0.75,
        whiteSpace: "nowrap",
      }}
    >
      <Box component="span" sx={{ color: colors.color, mr: 0.5 }}>
        {label}
      </Box>
      {value}件
    </Box>
  );
}

function VulnTable({ rows, title, toneName, valueFor, valueHeader }) {
  const colors = tone(toneName);
  if (!rows.length) return null;

  return (
    <Box
      component="section"
      sx={{ border: `1px solid ${slate[200]}`, borderRadius: 2, overflow: "hidden" }}
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
          <Box component="span" sx={{ color: colors.color }}>
            {title}
          </Box>{" "}
          <Box component="span" sx={{ color: slate[500] }}>
            {rows.length}件
          </Box>
        </Typography>
      </Box>
      <TableContainer sx={{ maxHeight: 360 }}>
        <Table stickyHeader size="small" sx={{ minWidth: 640 }}>
          <TableHead>
            <TableRow>
              {["ID", "SSVC判断", valueHeader].map((header) => (
                <TableCell
                  key={header}
                  sx={{
                    bgcolor: slate[50],
                    borderBottomColor: slate[200],
                    color: slate[500],
                    fontSize: 12,
                    fontWeight: 800,
                    px: 2,
                    py: 1.5,
                  }}
                >
                  {header}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow hover key={row.id}>
                <TableCell
                  sx={{
                    ...compactText,
                    color: slate[950],
                    fontFamily: "monospace",
                    fontWeight: 800,
                    px: 2,
                    py: 1.5,
                  }}
                >
                  {row.id}
                </TableCell>
                <TableCell
                  sx={{
                    ...compactText,
                    color: tone(row.ssvcTone).color,
                    fontWeight: 900,
                    px: 2,
                    py: 1.5,
                  }}
                >
                  {row.ssvcDecision}
                </TableCell>
                <TableCell
                  sx={{
                    ...compactText,
                    color: slate[950],
                    fontFamily: row.status === "fixable" ? "monospace" : "inherit",
                    fontWeight: 700,
                    px: 2,
                    py: 1.5,
                  }}
                >
                  {valueFor(row)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

function MobileVulnGroup({ dependency, rows, title, toneName, valueFor, valueLabel }) {
  const colors = tone(toneName);
  if (!rows.length) return null;

  return (
    <Box
      component="section"
      sx={{ border: `1px solid ${slate[200]}`, borderRadius: 2, bgcolor: "white", p: 1.5 }}
    >
      <Typography sx={{ color: slate[950], fontSize: 14, fontWeight: 900, px: 0.5 }}>
        <Box component="span" sx={{ color: colors.color }}>
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
            sx={{ bgcolor: "white", border: `1px solid ${slate[200]}`, borderRadius: 1.5, p: 2 }}
          >
            <Stack direction="row" gap={1.5} justifyContent="space-between">
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
                  color: tone(row.ssvcTone).color,
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
              sx={{ borderTop: `1px solid ${slate[200]}`, mt: 2, pt: 1.5, textAlign: "center" }}
            >
              <Grid size={6} sx={{ borderRight: `1px solid ${slate[200]}`, px: 1 }}>
                <Typography sx={{ color: slate[500], fontSize: 11, fontWeight: 800 }}>
                  SSVC
                </Typography>
                <Typography
                  sx={{ color: tone(row.ssvcTone).color, fontSize: 12, fontWeight: 900, mt: 0.5 }}
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

function DependencyPathPanel({ dependency }) {
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
            sx={{ bgcolor: "white", border: `1px solid ${slate[200]}`, borderRadius: 2, p: 2 }}
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
              <OsPackageChip type={occurrence.type} />
            </Stack>
            <Box
              sx={{
                bgcolor: slate[50],
                borderRadius: 1.5,
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

function DetailView({ dependency, onBack }) {
  const [tab, setTab] = useState("vulns");
  const rows = useMemo(() => buildVulns(dependency), [dependency]);

  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <Button
          onClick={onBack}
          sx={{
            ...buttonSx,
            bgcolor: "white",
            borderColor: slate[200],
            color: slate[700],
            minHeight: 40,
            "&:hover": { bgcolor: slate[50], borderColor: slate[200] },
          }}
          variant="outlined"
        >
          ← 一覧へ
        </Button>
      </Box>
      <DetailSummary dependency={dependency} />
      <RecommendationSection dependency={dependency} />
      <DetailTabs dependency={dependency} onTabChange={setTab} rows={rows} tab={tab} />
    </Box>
  );
}

function SBOMDependencyRemediationPreview({ initialDependencyKey, initialView = "list" }) {
  const dependencies = useMemo(() => groupSbomEntries(sbomEntries), []);
  const [selectedKey, setSelectedKey] = useState(initialDependencyKey ?? dependencies[0]?.key);
  const [view, setView] = useState(initialView);
  const selectedDependency =
    dependencies.find((dependency) => dependency.key === selectedKey) ?? dependencies[0];

  return (
    <Box sx={shellSx}>
      <Box sx={pageSx}>
        {view === "list" ? (
          <ListView
            dependencies={dependencies}
            onOpen={(dependencyKeyValue) => {
              setSelectedKey(dependencyKeyValue);
              setView("detail");
            }}
          />
        ) : (
          <DetailView dependency={selectedDependency} onBack={() => setView("list")} />
        )}
      </Box>
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
