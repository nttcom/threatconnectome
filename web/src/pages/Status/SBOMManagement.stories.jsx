import { SBOMManagement } from "./SBOMManagement";
import { createDefaultSboms } from "./SBOMManagement.stories.helpers";

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

export const Default = {
  args: {
    initialSboms: createDefaultSboms(),
  },
};

export const EmptyState = {
  args: {
    initialSboms: [],
  },
};
