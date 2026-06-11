import { LanguageSwitcher } from "../../../components/LanguageSwitcher";
import { buildTopbarPageItems } from "../../../utils/App/topbarNavigation";

import { TopbarView } from "./TopbarView";

const fixtureTranslations = {
  "pages.sbomManagement": "SBOM Management",
  "pages.sbomShort": "SBOM",
  "pages.teamManagement": "Team Management",
  "pages.vulnerabilities": "Vulnerabilities",
  "pages.eol": "EOL",
  "pages.todo": "ToDo",
};

const pageItems = buildTopbarPageItems((key) => fixtureTranslations[key]);
const teamItems = [
  { id: "security", name: "Security Team", current: true },
  { id: "platform", name: "Platform Team" },
  { id: "product", name: "Product Team" },
  { id: "backend", name: "Backend Team" },
  { id: "frontend", name: "Frontend Team" },
  { id: "sre", name: "SRE Team" },
  { id: "incident-response", name: "Incident Response Team" },
  { id: "cloud-infrastructure", name: "Cloud Infrastructure Team" },
  { id: "identity-access", name: "Identity Access Team" },
  { id: "compliance", name: "Compliance Team" },
  { id: "devsecops", name: "DevSecOps Team" },
  { id: "data-protection", name: "Data Protection Team" },
  { id: "mobile-app", name: "Mobile App Team" },
  { id: "partner-integration", name: "Partner Integration Team" },
];

const labels = {
  createTeam: "Create Team",
  current: "Current",
  currentTeamDetail: "Switch the current team",
  homeAriaLabel: "Threatconnectome home",
  logout: "Logout",
  noTeam: "No team",
  pageMenu: "Page menu",
  pageSwitch: "Switch page",
  settings: "Settings",
  teamMenu: "Team menu",
  teamSelect: "Select team",
  userMenu: "User menu",
};

function ThreatconnectomeTopbarMuiStory() {
  return (
    <TopbarView
      currentPage={pageItems[0]}
      currentTeam={teamItems[0]}
      labels={labels}
      languageSwitcher={<LanguageSwitcher />}
      onCreateTeam={() => undefined}
      onLogout={() => undefined}
      onOpenAccountSettings={() => undefined}
      onSelectHome={(event) => event.preventDefault()}
      onSelectPage={() => undefined}
      onSelectTeam={() => undefined}
      pageItems={pageItems}
      teamItems={teamItems}
    />
  );
}

const meta = {
  title: "Threatconnectome/Topbar MUI",
  component: ThreatconnectomeTopbarMuiStory,
  parameters: {
    layout: "fullscreen",
  },
};

export default meta;

export const Default = {
  render: () => <ThreatconnectomeTopbarMuiStory />,
};
