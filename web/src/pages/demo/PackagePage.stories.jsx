import PackagePage from "./PackagePage";
// 全てのmockデータをインポート
import {
  mockVulnerabilities,
  mockMembers,
  mockPackageData,
  mockPackageReferences,
  mockDefaultSafetyImpact,
  mockSsvcCounts,
  mockTabCounts,
} from "./mockData";

export default {
  title: "demo/PackagePage",
  component: PackagePage,
  parameters: {
    layout: "fullscreen",
  },
  // argTypesは最新のpropsを反映
  argTypes: {
    packageData: { control: "object" },
    packageReferences: { control: "object" },
    defaultSafetyImpact: { control: "text" },
    ssvcCounts: { control: "object" },
    tabCounts: { control: "object" },
    initialVulnerabilities: { control: "object" },
    members: { control: "object" },
  },
};

const Template = (args) => <PackagePage {...args} />;

// Defaultストーリー
export const Default = Template.bind({});
Default.args = {
  packageData: mockPackageData,
  packageReferences: mockPackageReferences,
  defaultSafetyImpact: mockDefaultSafetyImpact,
  ssvcCounts: mockSsvcCounts,
  tabCounts: mockTabCounts,
  initialVulnerabilities: mockVulnerabilities,
  members: mockMembers,
};

// EmptyStateストーリー
export const EmptyState = Template.bind({});
EmptyState.args = {
  ...Default.args,
  packageReferences: [],
  initialVulnerabilities: [],
  ssvcCounts: { immediate: 0, high: 0, medium: 0, low: 0 },
  tabCounts: { unsolved: 0, solved: 42 },
};

// WithPaginationストーリー
export const WithPagination = Template.bind({});
const manyVulnerabilities = [
  ...mockVulnerabilities,
  ...Array.from({ length: 15 }, (_, i) => ({
    id: `vuln-extra-${i}`,
    title: `Additional Vulnerability ${i + 1}`,
    highestSsvc: "medium",
    updated_at: "2025-09-01",
    affected_versions: ["1.0.0"],
    patched_versions: ["1.0.1"],
    // --- クリック時にエラーが出ないよう、詳細情報を追加 ---
    cveId: `CVE-2025-EXTRA-${i}`,
    description: "This is a generated description for testing pagination.",
    mitigation: "Generated mitigation advice.",
    tasks: [], // タスク0件のケースをテスト
  })),
];
WithPagination.args = {
  ...Default.args,
  initialVulnerabilities: manyVulnerabilities,
  tabCounts: { unsolved: manyVulnerabilities.length, solved: 42 },
};
