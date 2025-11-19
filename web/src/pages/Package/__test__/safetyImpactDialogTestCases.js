// safetyImpactDialogTestCases.js
import userEvent from "@testing-library/user-event";

import { fireEvent, screen } from "../../../utils/__tests__/test-utils";

import { MOCK_VULN_IDS_UNSOLVED } from "./apiMocks";

export async function testSafetyImpactDialog(option, mockUpdateTicket) {
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
}
