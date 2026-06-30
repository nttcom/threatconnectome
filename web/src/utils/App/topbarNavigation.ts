import ChecklistIcon from "@mui/icons-material/Checklist";
import EventNoteIcon from "@mui/icons-material/EventNote";
import GppMaybeIcon from "@mui/icons-material/GppMaybe";
import GroupIcon from "@mui/icons-material/Group";
import Inventory2Icon from "@mui/icons-material/Inventory2";
import type { Location } from "react-router-dom";

import { LocationReader } from "../LocationReader";
import { preserveParams } from "../urlUtils";
import type { TopbarPageItem } from "../../pages/App/Topbar/topbarTypes";

type TopbarPageDefinition = Omit<TopbarPageItem, "label" | "shortLabel"> & {
  labelKey: string;
  shortLabelKey?: string;
};

export const topbarPageDefinitions: TopbarPageDefinition[] = [
  {
    id: "sbomManagement",
    labelKey: "pages.sbomManagement",
    shortLabelKey: "pages.sbomShort",
    icon: Inventory2Icon,
    tone: "brand",
    to: "/",
    isCurrent: (locationReader) => locationReader.isStatusPage() || locationReader.isPackagePage(),
  },
  {
    id: "teamManagement",
    labelKey: "pages.teamManagement",
    icon: GroupIcon,
    tone: "sky",
    to: "/pteam",
    isCurrent: (locationReader) => locationReader.isPTeamPage(),
  },
  {
    id: "vulnerabilities",
    labelKey: "pages.vulnerabilities",
    icon: GppMaybeIcon,
    tone: "red",
    to: "/vulns",
    isCurrent: (locationReader) => locationReader.isVulnsPage(),
  },
  {
    id: "eol",
    labelKey: "pages.eol",
    icon: EventNoteIcon,
    tone: "amber",
    to: "/eol",
    isCurrent: (locationReader, location) =>
      locationReader.isEoLPage() || location.pathname.startsWith("/supported-products"),
  },
  {
    id: "todo",
    labelKey: "pages.todo",
    icon: ChecklistIcon,
    tone: "violet",
    to: "/todo",
    isCurrent: (locationReader) => locationReader.isToDoPage(),
  },
];

export function buildTopbarPageItems(t: (key: string) => string): TopbarPageItem[] {
  return topbarPageDefinitions.map((item) => ({
    ...item,
    label: t(item.labelKey),
    shortLabel: item.shortLabelKey ? t(item.shortLabelKey) : undefined,
  }));
}

export function getCurrentTopbarPage(location: Location, pageItems: TopbarPageItem[]) {
  const locationReader = new LocationReader(location);
  return pageItems.find((item) => item.isCurrent(locationReader, location)) ?? pageItems[0];
}

export function buildTopbarPageUrl(locationSearch: string, page: TopbarPageItem) {
  const cleanedQueryParams = preserveParams(locationSearch).toString();
  return cleanedQueryParams ? `${page.to}?${cleanedQueryParams}` : page.to;
}
