import type { Meta, StoryObj } from "@storybook/react-vite";
import { ServiceEolDashboard } from "./ServiceEolDashboardPage";
import {
  MOCK_SERVICES,
  MOCK_SERVICES_EXPIRED_ONLY,
  MOCK_SERVICES_SAFE_ONLY,
  MOCK_SERVICES_EMPTY,
  MOCK_SERVICES_MANY,
  MOCK_LAST_UPDATED,
} from "./mocks/serviceData";

const meta = {
  title: "Eol/ServiceEolDashboard",
  component: ServiceEolDashboard,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ServiceEolDashboard>;

export default meta;
type Story = StoryObj<typeof meta>;

// 標準的なデータを表示
export const Default: Story = {
  args: {
    services: MOCK_SERVICES,
    lastUpdated: MOCK_LAST_UPDATED,
  },
};

// 期限切れのツールのみ
export const ExpiredOnly: Story = {
  args: {
    services: MOCK_SERVICES_EXPIRED_ONLY,
    lastUpdated: MOCK_LAST_UPDATED,
  },
};

// サポート中のツールのみ
export const SafeOnly: Story = {
  args: {
    services: MOCK_SERVICES_SAFE_ONLY,
    lastUpdated: MOCK_LAST_UPDATED,
  },
};

// データなし（空の状態）
export const Empty: Story = {
  args: {
    services: MOCK_SERVICES_EMPTY,
    lastUpdated: MOCK_LAST_UPDATED,
  },
};

// 大量データ
export const ManyItems: Story = {
  args: {
    services: MOCK_SERVICES_MANY,
    lastUpdated: MOCK_LAST_UPDATED,
  },
};
