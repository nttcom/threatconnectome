import { SBOMManagement } from "./SBOMManagement";

const meta = {
  argTypes: {
    initialActiveId: { control: false },
    initialSboms: { control: false },
  },
  component: SBOMManagement,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
};

export default meta;

export const Default = {};

export const EmptyState = {
  args: {
    initialSboms: [],
  },
};
