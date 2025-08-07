import ArticleIcon from "@mui/icons-material/Article";
import DirectionsRunIcon from "@mui/icons-material/DirectionsRun";
import DnsIcon from "@mui/icons-material/Dns";
import FindInPageIcon from "@mui/icons-material/FindInPage";
import LocalFireDepartmentIcon from "@mui/icons-material/LocalFireDepartment";
import PeopleIcon from "@mui/icons-material/People";
import StopCircleIcon from "@mui/icons-material/StopCircle";
import StorageIcon from "@mui/icons-material/Storage";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Tab,
  Tabs,
  Typography,
  Divider,
} from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { CustomTabPanel } from "../../components/CustomTabPanel";

// --- データ定義 ---
// 本来はAI分析エンジンのAPIから取得しますが、ここではUI表示用のダミーデータとして定義します。

// 「脅威シナリオ」タブに表示されるデータ
const threatScenarios = [
  {
    icon: <LocalFireDepartmentIcon />,
    title: "Data Center Fire",
    description:
      "A compromised server's cooling system could be disabled, leading to overheating and a potential fire, causing catastrophic physical damage.",
  },
  {
    icon: <FindInPageIcon />,
    title: "Complete Data Exfiltration",
    description:
      "The vulnerability allows attackers to gain root access, bypassing all security measures to steal sensitive customer and corporate data.",
  },
];

// 「影響を受ける資産」タブに表示されるデータ
const affectedAssets = [
  {
    icon: <DnsIcon />, // サーバーを表すアイコン
    name: "Production Web Servers (web-prod-01, web-prod-02)",
    impact: "Directly vulnerable. Can be used as an entry point for system takeover.",
  },
  {
    icon: <StorageIcon />, // データベースを表すアイコン
    name: "Customer Database (customer-db-main)",
    impact: "At risk of data exfiltration or ransom attacks via compromised web servers.",
  },
  {
    icon: <PeopleIcon />, // 人（ユーザー）を表すアイコン
    name: "End Users & Customers",
    impact: "Personal Identifiable Information (PII) is at high risk of being leaked.",
  },
];

// 「分析の根拠」タブに表示されるデータ
const analysisBasis = {
  dataSources: [
    "NVD (CVE-2021-44228 Entry)",
    "Internal System Architecture Documents (ver 2.1)",
    "Past Incident Reports (INC-2020-115)",
  ],
  reasoning:
    "The AI model identified a direct network path from the vulnerable public-facing servers to the primary customer database. This, combined with historical data from similar Log4j incidents, indicates a high probability of a data breach scenario.",
};

// AIリスク分析画面のメインコンポーネント
export function AIRiskAnalysis() {
  // 現在選択されているタブの状態を管理します (初期値は0番目のタブ)
  const [tabValue, setTabValue] = useState(0);

  // ユーザーがタブをクリックしたときに呼ばれ、表示するタブを切り替えます
  const handleAITabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  return (
    <>
      {/* --- ヘッダー部分 --- */}
      {/* このセクションは、何の分析画面なのかをユーザーに明確に伝えます */}
      <Box sx={{ mb: 4 }}>
        {/* h4: ページのメインタイトル。脆弱性IDなど最も重要な情報を表示 */}
        <Typography variant="h4" component="h1" gutterBottom>
          AI Risk Analysis: CVE-2021-4228 (Log4Shell)
        </Typography>
        {/* Box: 関連情報を横並びに表示するためのコンテナ */}
        <Box sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}>
          {/* Typography: 影響を受けるサービスやターゲットといった補足情報を表示 */}
          <Typography variant="body1" color="text.secondary">
            Service: myADV 2023
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Target: ubuntu-20.04
          </Typography>
          {/* Typography: CVSSスコアをラベル付きのテキストで表示 */}
          <Typography variant="body1" color="text.secondary">
            CVSS: 9.8
          </Typography>
        </Box>
      </Box>

      {/* --- メインコンテンツ --- */}
      {/* Paper: 分析結果全体を囲むコンテナ。影(elevation)で浮き上がって見え、情報のまとまりを示します */}
      <Paper elevation={3} sx={{ p: 4, borderRadius: 4 }}>
        {/* Grid: レスポンシブなレイアウトを組むためのコンテナ */}
        <Grid container spacing={4}>
          {/* --- リスクサマリー --- */}
          {/* ユーザーが最初に目にする、最も重要な情報の要約セクション */}
          <Grid item xs={12}>
            {/* Box: タイトルとアイコンを横に並べるためのコンテナ */}
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              {/* WarningAmberIcon: 警告アイコンで、このセクションの重要性を示唆します */}
              <Box>
                <WarningAmberIcon sx={{ fontSize: 40, color: "error.main" }} />
              </Box>
              {/* Typography: セクションのタイトル */}
              <Typography variant="h5" component="h2" gutterBottom>
                Risk Summary
              </Typography>
            </Box>
            {/* List: 発生しうる被害の種類を一覧で表示。ユーザーはここで全体像を把握します */}
            <List>
              {/* ListItem: 各被害項目 */}
              <ListItem>
                {/*ListItemIcon: アイコンを表示し、視覚的な理解を助けます*/}
                <ListItemIcon>
                  <LocalFireDepartmentIcon />
                </ListItemIcon>
                {/* ListItemText: 被害内容のテキスト */}
                <ListItemText primary="Fire" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <StopCircleIcon />
                </ListItemIcon>
                <ListItemText primary="Service Disruption" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <DirectionsRunIcon />
                </ListItemIcon>
                <ListItemText primary="System Takeover" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <FindInPageIcon />
                </ListItemIcon>
                <ListItemText primary="Data Breach" />
              </ListItem>
            </List>
            {/* Typography: AIによる総括。このリスクの最も重要な結論を短い文章で伝えます */}
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              High risk of server compromise leading to complete data exfiltration.
            </Typography>
          </Grid>

          {/* --- 詳細分析 --- */}
          {/* サマリーで概要を掴んだユーザーが、さらに詳しい情報を確認するためのセクション */}
          <Grid item xs={12}>
            {/* Box: タブナビゲーションのコンテナ。下線でタブエリアを区切ります */}
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              {/* Tabs: 複数の情報パネルを切り替えるためのナビゲーションUI */}
              <Tabs
                value={tabValue}
                variant="scrollable" // 画面が狭い時にスクロール可能にする
                scrollButtons="auto"
                onChange={handleAITabChange}
                aria-label="detailed analysis tabs"
              >
                {/* Tab: クリック可能なタブのラベル */}
                <Tab label="Threat Scenarios" />
                <Tab label="Affected Assets" />
                <Tab label="Analysis Basis" />
              </Tabs>
            </Box>
            {/* CustomTabPanel: 選択中のタブに対応するコンテンツを表示します (index 0) */}
            <CustomTabPanel value={tabValue} index={0}>
              {/* Grid: 複数のシナリオカードを並べるためのレイアウトコンテナ */}
              <Grid container spacing={2}>
                {/* threatScenarios配列の各要素をループ処理して、シナリオカードを動的に生成します */}
                {threatScenarios.map((scenario, index) => (
                  <Grid item xs={12} key={index}>
                    {/* Card: 各シナリオを１つのカードとして表示し、情報を区切ります */}
                    <Card variant="outlined">
                      {/* CardHeader: カードのヘッダー。アイコンとタイトルを表示 */}
                      <CardHeader
                        avatar={<Avatar sx={{ bgcolor: "error.main" }}>{scenario.icon}</Avatar>}
                        title={scenario.title}
                        titleTypographyProps={{ variant: "h6" }}
                      />
                      {/* CardContent: カードの本文。シナリオの詳細な説明を表示 */}
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          {scenario.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CustomTabPanel>

            {/* CustomTabPanel: 「影響を受ける資産」タブのコンテンツ (index 1) */}
            <CustomTabPanel value={tabValue} index={1}>
              {/* Typography: このタブセクションのタイトル */}
              <Typography variant="h6" gutterBottom>
                Potentially Affected Assets
              </Typography>
              {/* List: 影響を受ける可能性のある資産を一覧表示します */}
              <List>
                {affectedAssets.map((asset, index) => (
                  // ListItem: 各資産の情報。dividerで項目間に区切り線を入れます
                  <ListItem key={index} divider={index < affectedAssets.length - 1}>
                    {/* ListItemIcon: 資産の種類を表すアイコン */}
                    <ListItemIcon sx={{ minWidth: 40 }}>{asset.icon}</ListItemIcon>
                    {/* ListItemText: primaryに資産名、secondaryに影響の詳細を表示 */}
                    <ListItemText primary={asset.name} secondary={asset.impact} />
                  </ListItem>
                ))}
              </List>
            </CustomTabPanel>

            {/* CustomTabPanel: 「分析の根拠」タブのコンテンツ (index 2) */}
            <CustomTabPanel value={tabValue} index={2}>
              <Box>
                {/* Typography: 「AIの思考ロジック」セクションのタイトル */}
                <Typography variant="h6" gutterBottom>
                  Reasoning Logic
                </Typography>
                {/* Typography: AIがなぜこの結論に至ったのかを平易な言葉で説明し、ユーザーの信頼性を高めます */}
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {analysisBasis.reasoning}
                </Typography>

                {/* Divider: セクション間の視覚的な区切り線 */}
                <Divider sx={{ my: 2 }} />

                {/* Typography: 「参照データソース」セクションのタイトル */}
                <Typography variant="h6" gutterBottom>
                  Data Sources
                </Typography>
                {/* List: AIが分析に使用したデータソースを一覧化し、分析の透明性を示します */}
                <List dense>
                  {analysisBasis.dataSources.map((source, index) => (
                    <ListItem key={index}>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <ArticleIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={source} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </CustomTabPanel>
          </Grid>
        </Grid>

        {/* --- フッター: アクションボタン --- */}
        {/* ユーザーが分析結果を確認した後に取るべき行動を提示します */}
        <Box sx={{ mt: 4, display: "flex", justifyContent: "flex-end", gap: 2 }}>
          {/* Button (outlined): 副次的なアクション。レポート出力など */}
          <Button variant="outlined">Export Report (PDF)</Button>
          {/* Button (contained): 主要なアクション。修正チケットの作成など、次に繋がる行動を促します */}
          <Button variant="contained">Create Response Ticket</Button>
        </Box>
      </Paper>
    </>
  );
}

// PropTypes: このコンポーネントが受け取るべきpropsの型を定義します。
// これにより、開発中のエラー検知や、コンポーネントの仕様理解が容易になります。
AIRiskAnalysis.propTypes = {
  tabValue: PropTypes.number.isRequired,
  handleAITabChange: PropTypes.func.isRequired,
  threatScenarios: PropTypes.arrayOf(
    PropTypes.shape({
      icon: PropTypes.element.isRequired,
      title: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
    }),
  ).isRequired,
};
