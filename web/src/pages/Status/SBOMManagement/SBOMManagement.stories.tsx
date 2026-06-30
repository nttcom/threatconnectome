import type { Meta, StoryObj } from "@storybook/react-vite";

import { SBOMManagement } from "./SBOMManagement";
import { createDefaultSboms } from "./SBOMManagement.stories.helpers";

const defaultSboms = createDefaultSboms();
const defaultService = defaultSboms[0];
const { dependencies: defaultDependencies, ...defaultCurrentService } = defaultService;

const meta = {
  argTypes: {
    currentDependencies: { control: false },
    currentService: { control: false },
    serviceTabs: { control: false },
  },
  component: SBOMManagement,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof SBOMManagement>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    currentDependencies: defaultDependencies,
    currentService: defaultCurrentService,
    pteamId: "storybook-pteam",
    serviceTabs: defaultSboms.map((sbom) => ({ id: sbom.id, title: sbom.title })),
  },
};

export const EmptyState: Story = {
  args: {
    currentDependencies: [],
    currentService: null,
    pteamId: "storybook-pteam",
    serviceTabs: [],
  },
};
