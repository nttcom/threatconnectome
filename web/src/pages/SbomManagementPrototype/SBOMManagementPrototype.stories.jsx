import { SBOMManagementPrototype } from "./SBOMManagementPrototype";

const meta = {
  argTypes: {
    initialActiveId: { control: false },
    initialSboms: { control: false },
  },
  component: SBOMManagementPrototype,
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
