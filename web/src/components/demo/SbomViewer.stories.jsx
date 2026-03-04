import SbomViewer from "./SbomViewer";

export default {
  title: "Demo/SbomViewer",
  component: SbomViewer,
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
    // MUIのデコレーターを無効化して、Tailwind CSSのスタイルのみを使用
    redux: { preloadedState: {} },
  },
  decorators: [
    (Story) => (
      <div style={{ width: "100%", height: "100vh" }}>
        <Story />
      </div>
    ),
  ],
};

/**
 * SBOM Viewerのデモアプリケーション
 * 
 * このコンポーネントは以下の機能を提供します:
 * - タブ形式で複数のSBOMファイルを管理
 * - 擬似的な非同期読み込み処理（3〜8秒のランダムな待機時間）
 * - ローディング中の誠実なメッセージ表示
 * - ライブラリの検索機能
 * - トースト通知による完了通知
 * 
 * 使い方:
 * 1. 「最初のSBOMを追加する」ボタンまたは「+」タブをクリック
 * 2. ローディングが完了するまで待機（または他のタブを追加して並行処理）
 * 3. 完了したタブのライブラリ一覧を確認
 * 4. 検索バーでライブラリを絞り込み
 */
export const Default = {
  args: {},
};
