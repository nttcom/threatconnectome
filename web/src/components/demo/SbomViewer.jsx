import { Plus, X, Package, Loader2, Search, FileJson, CheckCircle2, Info } from "lucide-react";
import { useState } from "react";

// ダミーデータを生成する関数
const generateDummyData = () => {
  const libraries = [
    { name: "react", version: "18.2.0", license: "MIT" },
    { name: "react-dom", version: "18.2.0", license: "MIT" },
    { name: "lodash", version: "4.17.21", license: "MIT" },
    { name: "axios", version: "1.6.0", license: "MIT" },
    { name: "express", version: "4.18.2", license: "MIT" },
    { name: "moment", version: "2.29.4", license: "MIT" },
    { name: "uuid", version: "9.0.1", license: "MIT" },
    { name: "chalk", version: "5.3.0", license: "MIT" },
    { name: "commander", version: "11.1.0", license: "MIT" },
    { name: "webpack", version: "5.89.0", license: "MIT" },
    { name: "typescript", version: "5.2.2", license: "Apache-2.0" },
    { name: "jest", version: "29.7.0", license: "MIT" },
    { name: "eslint", version: "8.52.0", license: "MIT" },
    { name: "prettier", version: "3.0.3", license: "MIT" },
    { name: "tailwindcss", version: "3.3.5", license: "MIT" },
  ];

  // ランダムに並び替えて、ランダムな件数を返す
  const shuffled = [...libraries].sort(() => 0.5 - Math.random());
  const count = Math.floor(Math.random() * 10) + 5; // 5〜15件
  return shuffled.slice(0, count).map((lib, index) => ({
    id: index,
    ...lib,
  }));
};

export default function SbomViewer() {
  const [tabs, setTabs] = useState([]);
  const [activeTabId, setActiveTabId] = useState(null);
  const [toasts, setToasts] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");

  // トースト通知を追加する関数
  const addToast = (message) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // SBOMを追加する（擬似的なアップロード処理）
  const handleAddSbom = () => {
    const newId = `sbom-${Date.now()}`;
    const newTab = {
      id: newId,
      name: `project-deps-${tabs.length + 1}.json`,
      status: "loading",
      data: null,
    };

    setTabs([...tabs, newTab]);
    setActiveTabId(newId);
    setSearchQuery(""); // 検索クエリをリセット

    // デモ用の擬似的な非同期処理（3秒〜8秒のランダムな待機）
    const processTime = Math.floor(Math.random() * 5000) + 3000;

    setTimeout(() => {
      setTabs((prevTabs) =>
        prevTabs.map((tab) => {
          if (tab.id === newId) {
            return {
              ...tab,
              status: "completed",
              data: generateDummyData(),
            };
          }
          return tab;
        }),
      );
      addToast(`🎉 ${newTab.name} の解析が完了しました`);
    }, processTime);
  };

  // タブを閉じる
  const handleCloseTab = (e, idToClose) => {
    e.stopPropagation();
    const newTabs = tabs.filter((tab) => tab.id !== idToClose);
    setTabs(newTabs);

    // アクティブなタブを閉じた場合、別のタブをアクティブにする
    if (activeTabId === idToClose) {
      setActiveTabId(newTabs.length > 0 ? newTabs[newTabs.length - 1].id : null);
    }
  };

  const activeTab = tabs.find((tab) => tab.id === activeTabId);

  // 検索フィルター
  const filteredData =
    activeTab?.data?.filter((item) =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase()),
    ) || [];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-800">
      {/* ヘッダー */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Package className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">SBOM Viewer</h1>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* タブバー */}
        <div className="bg-gray-100 border-b border-gray-200 flex items-center px-2 pt-2 overflow-x-auto">
          {tabs.map((tab) => (
            <div
              key={tab.id}
              onClick={() => {
                setActiveTabId(tab.id);
                setSearchQuery("");
              }}
              className={`
                group flex items-center gap-2 px-4 py-2.5 min-w-[180px] max-w-[240px] cursor-pointer
                border-t border-x rounded-t-lg text-sm transition-colors duration-150 relative
                ${
                  activeTabId === tab.id
                    ? "bg-white border-gray-200 text-blue-600 font-medium z-10"
                    : "bg-transparent border-transparent text-gray-500 hover:bg-gray-200"
                }
              `}
              style={{ marginBottom: activeTabId === tab.id ? "-1px" : "0" }}
            >
              {/* ステータスアイコン */}
              {tab.status === "loading" ? (
                <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
              ) : (
                <FileJson className="w-4 h-4 text-gray-400 group-hover:text-gray-600" />
              )}

              <span className="truncate flex-1">{tab.name}</span>

              {/* 閉じるボタン */}
              <button
                onClick={(e) => handleCloseTab(e, tab.id)}
                className="p-0.5 rounded-md hover:bg-gray-200 text-gray-400 hover:text-gray-700 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}

          {/* 追加(+)ボタンタブ */}
          <button
            onClick={handleAddSbom}
            className="flex items-center justify-center w-10 h-10 ml-1 rounded-t-lg text-gray-500 hover:bg-gray-200 hover:text-gray-800 transition-colors mb-[-1px]"
            title="SBOMを追加"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        {/* タブコンテンツエリア */}
        <div className="flex-1 overflow-auto bg-white">
          {!activeTab ? (
            // タブが一つもない時の空状態
            <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-4">
              <Package className="w-16 h-16 opacity-20" />
              <p className="text-lg">SBOMファイルがありません</p>
              <button
                onClick={handleAddSbom}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors shadow-sm"
              >
                <Plus className="w-4 h-4" />
                最初のSBOMを追加する
              </button>
            </div>
          ) : activeTab.status === "loading" ? (
            // ローディング中のUI（誠実なメッセージ表示）
            <div className="flex flex-col items-center justify-center h-full max-w-md mx-auto text-center px-4 space-y-6">
              <div className="relative">
                <div className="absolute inset-0 bg-blue-100 rounded-full animate-ping opacity-75"></div>
                <div className="relative bg-white p-4 rounded-full shadow-sm border border-gray-100">
                  <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
                </div>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-2">
                  SBOMを解析しています...
                </h2>
                <div className="bg-blue-50 text-blue-800 text-sm p-4 rounded-lg flex items-start text-left gap-3 border border-blue-100">
                  <Info className="w-5 h-5 flex-shrink-0 mt-0.5 text-blue-600" />
                  <p className="leading-relaxed">
                    ファイルサイズや依存関係の複雑さにより、完了まで数分程度かかる場合があります。
                    <br />
                    <strong>
                      このままお待ちいただくか、他のタブを開いて別の作業を進めることも可能です。
                    </strong>
                    解析が完了すると通知でお知らせします。
                  </p>
                </div>
              </div>
            </div>
          ) : (
            // 完了時のテーブルUI
            <div className="p-6 max-w-6xl mx-auto h-full flex flex-col">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                  {activeTab.name}
                  <span className="text-sm font-normal text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                    {activeTab.data.length} components
                  </span>
                </h2>

                {/* 検索バー */}
                <div className="relative">
                  <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="ライブラリを検索..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64 shadow-sm"
                  />
                </div>
              </div>

              {/* テーブル */}
              <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden flex-1 flex flex-col">
                <div className="overflow-auto flex-1">
                  <table className="min-w-full divide-y divide-gray-200 relative">
                    <thead className="bg-gray-50 sticky top-0 z-10">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          コンポーネント名
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          バージョン
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          ライセンス
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredData.length > 0 ? (
                        filteredData.map((lib) => (
                          <tr key={lib.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <Package className="w-4 h-4 text-gray-400 mr-2" />
                                <span className="font-medium text-gray-900">{lib.name}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {lib.version}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800 border border-gray-200">
                                {lib.license}
                              </span>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="3" className="px-6 py-12 text-center text-gray-500">
                            「{searchQuery}」に一致するライブラリは見つかりませんでした。
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* トースト通知エリア */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className="bg-gray-900 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 min-w-[300px] transform transition-all duration-300 translate-y-0 opacity-100"
          >
            <CheckCircle2 className="w-5 h-5 text-green-400" />
            <span className="text-sm font-medium">{toast.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
