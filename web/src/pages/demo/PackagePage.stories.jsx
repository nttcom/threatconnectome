import PackagePage from "./PackagePage";
// モックデータをインポート
import { mockVulnerabilities, mockMembers } from "./mockData";

export default {
  title: "demo/PackagePage",
  component: PackagePage,
  parameters: {
    // StorybookのUI上でコンポーネントが全画面表示されるように設定
    layout: "fullscreen",
  },
  argTypes: {
    // onSaveChangesが呼び出されたときにActionsパネルにログを出力する
    onSaveChanges: { action: "onSaveChanges" },
  },
};

// デフォルトのストーリー（データがある場合）
export const Default = {
  args: {
    // initialVulnerabilitiesとmembersをpropsとして渡す
    initialVulnerabilities: mockVulnerabilities,
    members: mockMembers,
  },
};

// データが空の場合のストーリー
export const EmptyState = {
  args: {
    initialVulnerabilities: [],
    members: mockMembers,
  },
};

// ページネーションをテストするために多くのデータを持つストーリー
export const WithPagination = {
  args: {
    initialVulnerabilities: [
      ...mockVulnerabilities,
      // 新しいデータを追加して1ページに収まらないようにする
      { id: "vuln-007", title: "Additional Vuln 1", tasks: [] },
      { id: "vuln-008", title: "Additional Vuln 2", tasks: [] },
      { id: "vuln-009", title: "Additional Vuln 3", tasks: [] },
    ],
    members: mockMembers,
  },
};
