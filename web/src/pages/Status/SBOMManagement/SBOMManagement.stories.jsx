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
};

export default meta;

export const Default = {
  args: {
    currentDependencies: defaultDependencies,
    currentService: defaultCurrentService,
    serviceTabs: defaultSboms.map((sbom) => ({ id: sbom.id, title: sbom.title })),
  },
};

export const EmptyState = {
  args: {
    currentDependencies: [],
    currentService: null,
    serviceTabs: [],
  },
};
