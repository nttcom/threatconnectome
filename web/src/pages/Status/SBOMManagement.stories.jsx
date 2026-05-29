import { SBOMManagement } from "./SBOMManagement";
import { createDefaultSboms } from "./SBOMManagement.stories.helpers";

const defaultSboms = createDefaultSboms();

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
    initialActiveId: defaultSboms[0].id,
    initialSboms: defaultSboms,
  },
};

export const EmptyState = {
  args: {
    initialSboms: [],
  },
};
