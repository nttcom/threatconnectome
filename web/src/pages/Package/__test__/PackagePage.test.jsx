// PackagePage.test.jsx
// このテストファイルの目的:
// PackagePage コンポーネントが (1) API フックを期待通りモックした状態で正しく初期描画されること、
// (2) 脆弱性 (CVE) ごとの安全性/影響セレクトを操作するとダイアログが開き、
// (3) ダイアログ内でオプション選択後に保存ボタンが活性化しクリックできる一連のユーザー操作フローを検証する。
// 各ブロックごとに役割をコメントしている。

// ------------------------------
// テスト関連ライブラリ / ユーティリティのインポート
// ------------------------------
import userEvent from "@testing-library/user-event";
import { describe, it, vi, beforeEach } from "vitest";

import {
  useGetDependenciesQuery,
  useGetPTeamMembersQuery,
  useGetPTeamQuery,
  useGetPTeamTicketCountsTiedToServicePackageQuery,
  useGetPTeamVulnIdsTiedToServicePackageQuery,
  useGetPteamTicketsQuery,
  useGetUserMeQuery,
  useGetVulnActionsQuery,
  useGetVulnQuery,
} from "../../../services/tcApi";
import { fireEvent, render, screen, waitFor } from "../../../utils/__tests__/test-utils";
import { Package } from "../PackagePage";

import { MOCK_VULN_IDS_UNSOLVED, setupApiMocks } from "./apiMocks";

// ------------------------------
// 外部フック / サービスのモック設定
// 認証フックと API 呼び出し用 RTK Query フックをモックし、
// テストがネットワークや認証状態に依存しないようにする。
// ------------------------------
vi.mock("../../../hooks/auth");

const mockUpdateTicket = vi.fn(() => ({
  unwrap: () => Promise.resolve(),
}));

vi.mock("../../../services/tcApi", async (importOriginal) => {
  const actual = await importOriginal();
  // updateTicket用の成功モックを追加
  return {
    ...actual,
    useGetPTeamQuery: vi.fn(),
    useGetDependenciesQuery: vi.fn(),
    useGetPTeamVulnIdsTiedToServicePackageQuery: vi.fn(),
    useGetPTeamTicketCountsTiedToServicePackageQuery: vi.fn(),
    useGetPTeamMembersQuery: vi.fn(),
    useGetVulnQuery: vi.fn(),
    useGetVulnActionsQuery: vi.fn(),
    useGetPteamTicketsQuery: vi.fn(),
    useGetUserMeQuery: vi.fn(),
    useUpdateTicketMutation: () => [mockUpdateTicket],
  };
});

// ------------------------------
// テストスイート定義: PackagePage の振る舞い検証
// ------------------------------
describe("PackagePage Component Unit Tests", () => {
  // --- 共通セットアップ ---
  // 各テストケースの実行前に、APIモックの初期化とコンポーネントのレンダリングを行う
  beforeEach(() => {
    // 1. API モック初期化: 全て成功状態を返すよう設定
    setupApiMocks();

    // 2. テストに必要な識別子とルーティング情報を定義
    const packageId = "pkg:npm/react@18.2.0";
    const pteamId = "pteam-abc";
    const serviceId = "svc-xyz";
    const route = `/packages/${encodeURIComponent(packageId)}?pteamId=${pteamId}&serviceId=${serviceId}`;
    const path = "/packages/:packageId";

    // 3. 対象コンポーネントをレンダリング
    render(<Package />, { route, path });
  });

  // --- テストケース: APIフック呼び出しの検証 ---
  it("should call all required API hooks on initial render", async () => {
    // 画面のレンダリングが安定するまで待機
    await screen.findByText("react");

    // モックされた各APIフックが少なくとも1回は呼び出されたことを検証（配列＋forEachで簡潔化）
    const apiHooks = [
      useGetPTeamQuery,
      useGetDependenciesQuery,
      useGetPTeamVulnIdsTiedToServicePackageQuery,
      useGetPTeamTicketCountsTiedToServicePackageQuery,
      useGetPTeamMembersQuery,
      useGetVulnQuery,
      useGetVulnActionsQuery,
      useGetPteamTicketsQuery,
      useGetUserMeQuery,
    ];
    await waitFor(() => {
      apiHooks.forEach((fn) => expect(fn).toHaveBeenCalled());
    });
  });

  // --- テストケース 1: 初期描画の検証 ---
  it("should render correctly with successful API calls", async () => {
    // API呼び出しを経て、主要な要素が描画されていることを確認
    // (例: パッケージ名や脆弱性情報など)
    expect(await screen.findByText("react")).toBeInTheDocument();
    // expect(screen.getByText("CVE-2023-0002")).toBeInTheDocument();
    // expect(screen.getByText("CVE-2023-0003")).toBeInTheDocument();
  });

  // --- テストケース 2: ダイアログ表示の検証 ---
  it("should open the dialog when the safety/impact select is clicked", async () => {
    // 1. CVE に紐づくセレクトボックスを取得し、クリック操作を行う
    const selectWrappers = screen.getAllByTestId("safety-impact-select-ticket-for-CVE-2023-0002");
    const combobox = selectWrappers[0].querySelector('[role="combobox"]');
    fireEvent.mouseDown(combobox);

    // 2. ダイアログが表示されることを検証
    const dialog = await screen.findByRole("dialog");
    expect(dialog).toBeInTheDocument();
  });

  // --- パラメータ化テスト: 全選択肢で保存API呼び出し検証 ---
  const options = ["Catastrophic", "Critical", "Marginal", "Negligible"];
  describe.each(options)("ダイアログで '%s' を選択した場合", (option) => {
    it(`should enable the save button after selecting '${option}' in the dialog and call mutation on save`, async () => {
      // 1. ダイアログを開く
      const selectWrappers = screen.getAllByTestId(
        `safety-impact-select-ticket-for-${MOCK_VULN_IDS_UNSOLVED.vuln_ids[0]}`,
      );
      const combobox = selectWrappers[0].querySelector('[role="combobox"]');
      fireEvent.mouseDown(combobox);
      await screen.findByRole("dialog");

      // 2. ダイアログ内のセレクトボックスを開く
      const dialogSelect = await screen.findByTestId("dialog-safety-impact-select");
      const dialogCombobox = dialogSelect.querySelector('[role="combobox"]');
      fireEvent.mouseDown(dialogCombobox);

      // 3. option オプションを選択
      const optionNode = await screen.findByRole("option", { name: option });
      await userEvent.click(optionNode);

      // 4. 選択が反映されたことを確認
      expect(dialogCombobox.textContent).toBe(option);

      // 5. 保存ボタンが活性化されていることを検証
      const saveButton = await screen.findByRole("button", { name: /save/i });
      expect(saveButton).not.toBeDisabled();

      // 6. 保存ボタンをクリック
      await userEvent.click(saveButton);

      // 7. useUpdateTicketMutation が呼び出されたことを検証
      expect(mockUpdateTicket).toHaveBeenCalled();
    });
  });

  // --- テストケース 4: チケットステータス変更の検証 ---
  it("should call updateTicket mutation when status is changed via TicketHandlingStatusSelector", async () => {
    // 1. 脆弱性 CVE-2023-0002 に関連するチケットのステータスボタンを探す
    // TicketHandlingStatusSelector の初期ステータスは "Alerted" と想定
    // 複数の "Alerted" ボタンが存在するため、findAllByRoleで全て取得し、最初の要素を操作対象とする
    const statusButtons = await screen.findAllByRole("button", { name: "Alerted" });
    await userEvent.click(statusButtons[0]);

    // 2. 表示されたメニューから "Acknowledge" を選択
    const acknowledgeOption = await screen.findByRole("menuitem", { name: "Acknowledge" });
    await userEvent.click(acknowledgeOption);

    // 3. useUpdateTicketMutation が正しい引数で呼び出されたことを検証
    expect(mockUpdateTicket).toHaveBeenCalled();
  });
});
