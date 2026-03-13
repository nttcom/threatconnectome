import { addHours } from "date-fns";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { InvitationManageDialog } from "./InvitationManageDialog";

const meta = {
  component: InvitationManageDialog,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component: `
チームへの招待リンクを発行・管理するダイアログコンポーネント。

**主な機能:**
- 発行済み招待リンクの一覧表示（有効・期限切れの状態表示）
- 新規招待リンクの作成（使用回数制限・有効期限の設定）
- リンクのコピー・無効化

**画面遷移:**
\`リスト画面\` → \`作成フォーム\` → \`作成完了\` → \`リスト画面\`
        `,
      },
    },
  },
  argTypes: {
    initialInvitations: {
      description: "初期表示する招待リンクのリスト（モック用）",
      control: false,
    },
  },
  args: {},
} satisfies Meta<typeof InvitationManageDialog>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * 有効なリンクと期限切れリンクが混在する通常状態。
 * ステータスバッジの色・テキストの違いと、コピー・無効化ボタンの動作を確認できる。
 */
export const ListWithInvitations: Story = {
  name: "リスト: 通常（複数リンク）",
  args: {
    initialInvitations: [
      {
        id: "1",
        link: "https://example.com/pteam/join?token=xt7k9p2m",
        limitCount: null,
        expiration: null,
        usedCount: 0,
      },
      {
        id: "2",
        link: "https://example.com/pteam/join?token=b4v9m1zq",
        limitCount: 5,
        expiration: addHours(new Date(), 24),
        usedCount: 2,
      },
    ],
  },
  parameters: {
    docs: {
      description: {
        story:
          "有効なリンクが2件の状態。無制限・期限なしのリンクと、回数制限・有効期限ありのリンクが並ぶ。「無効化」ボタンでリストからリンクを削除できる。",
      },
    },
  },
};

/**
 * 発行済みリンクが1件もない状態。
 * 空状態のメッセージが表示されることを確認する。
 */
export const ListEmpty: Story = {
  name: "リスト: 空（リンク0件）",
  args: {
    initialInvitations: [],
  },
  parameters: {
    docs: {
      description: {
        story:
          "招待リンクが1件も存在しない初期状態。「有効な招待リンクはありません」というメッセージが表示される。「新規作成」ボタンから作成フォームへ遷移できる。",
      },
    },
  },
};

/**
 * 大量のリンクが存在する場合のスクロール確認用。
 * レイアウト崩れが起きないことを確認する。
 */
export const ListManyInvitations: Story = {
  name: "リスト: 大量リンク（8件・スクロール確認）",
  args: {
    initialInvitations: Array.from({ length: 8 }, (_, i) => ({
      id: String(i + 1),
      link: `https://example.com/pteam/join?token=token${String(i + 1).padStart(4, "0")}`,
      limitCount: i % 3 === 0 ? null : (i + 1) * 2,
      expiration: i % 3 === 0 ? null : addHours(new Date(), (i + 1) * 12),
      usedCount: i,
    })),
  },
  parameters: {
    docs: {
      description: {
        story:
          "8件のリンクが存在する状態。有効・期限切れ・無制限・回数制限などが混在。ダイアログのスクロール動作とレイアウト崩れを確認する。",
      },
    },
  },
};

/**
 * 非常に長いURLが含まれるケース。
 * テキストが折り返し・省略されてレイアウトが崩れないことを確認する。
 */
export const ListLongUrl: Story = {
  name: "リスト: 長いURL（テキスト折り返し確認）",
  args: {
    initialInvitations: [
      {
        id: "1",
        link: "https://very-long-hostname.example.com/pteam/join?token=averylongtokenvaluethatmightoverflowtheuiifnothandledproperly",
        limitCount: null,
        expiration: addHours(new Date(), 24),
        usedCount: 0,
      },
    ],
  },
  parameters: {
    docs: {
      description: {
        story:
          "トークン部分が非常に長いURLの表示確認。`text-overflow: ellipsis` が機能してレイアウトが崩れないことを確認する。",
      },
    },
  },
};
