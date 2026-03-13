import type { Meta, StoryObj } from "@storybook/react-vite";

import { SBOMUploadProgress } from "./SBOMUploadProgress";

const meta = {
  component: SBOMUploadProgress,
} satisfies Meta<typeof SBOMUploadProgress>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Empty: Story = {
  args: { progresses: [] },
};

export const Single: Story = {
  args: {
    progresses: [
      { serviceName: "frontend", progressPercent: 45, estimatedCompletionTime: "14:32" },
    ],
  },
};

export const Multiple: Story = {
  args: {
    progresses: [
      { serviceName: "frontend", progressPercent: 45, estimatedCompletionTime: "14:32" },
      { serviceName: "backend", progressPercent: 80, estimatedCompletionTime: "14:28" },
      { serviceName: "mobile-app", progressPercent: 10, estimatedCompletionTime: "14:55" },
    ],
  },
};

export const JustStarted: Story = {
  args: {
    progresses: [{ serviceName: "frontend", progressPercent: 0, estimatedCompletionTime: "15:00" }],
  },
};

export const LongServiceName: Story = {
  args: {
    progresses: [
      {
        serviceName: "this-is-a-very-long-service-name-that-might-overflow-the-table-cell",
        progressPercent: 50,
        estimatedCompletionTime: "14:32",
      },
      {
        serviceName: "another-very-long-service-name-to-test-multiple-rows-with-long-names",
        progressPercent: 30,
        estimatedCompletionTime: "14:45",
      },
    ],
  },
};

export const LongSingleWord: Story = {
  args: {
    progresses: [
      {
        serviceName:
          "averylongservicenamethathasnospacesordashesandshouldoverflowthecontainerandkeepgoingwellbeyondanynormalservicenamelength",
        progressPercent: 50,
        estimatedCompletionTime: "14:32",
      },
      {
        serviceName: "anotherlongwordservicenamethatkeepsgoingandgoingwithoutanybreaks",
        progressPercent: 70,
        estimatedCompletionTime: "14:20",
      },
    ],
  },
};

export const ManyItems: Story = {
  args: {
    progresses: Array.from({ length: 20 }, (_, i) => ({
      serviceName: `service-${i + 1}`,
      progressPercent: Math.floor((i / 19) * 100),
      estimatedCompletionTime: `14:${String(i + 1).padStart(2, "0")}`,
    })),
  },
};
