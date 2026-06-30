import type { SvgIconComponent } from "@mui/icons-material";
import type { SxProps, Theme } from "@mui/material/styles";
import type { MouseEvent, ReactNode } from "react";
import type { Location } from "react-router-dom";

import type { LocationReader } from "../../../utils/LocationReader";

export type TopbarTone = "brand" | "sky" | "red" | "amber" | "violet" | "slate";

export type TopbarPageItem = {
  icon: SvgIconComponent;
  id: string;
  label: string;
  shortLabel?: string;
  tone: TopbarTone;
  to: string;
  isCurrent: (locationReader: LocationReader, location: Location) => boolean;
};

export type TopbarTeamItem = {
  current?: boolean;
  detail?: string;
  id: string;
  name: string;
};

export type TopbarLabels = {
  createTeam: string;
  current: string;
  currentTeamDetail: string;
  homeAriaLabel: string;
  logout: string;
  noTeam: string;
  pageMenu: string;
  pageSwitch: string;
  settings: string;
  teamMenu: string;
  teamSelect: string;
  userMenu: string;
};

export type MenuAnchor = HTMLElement | null;
export type MenuToggleHandler = (event: MouseEvent<HTMLElement>) => void;
export type Sx = SxProps<Theme>;
export type MenuWidth = { xs: string; sm: number };

export type TopbarViewProps = {
  currentPage: TopbarPageItem;
  currentTeam: TopbarTeamItem | null;
  hasUserMe: boolean;
  labels: TopbarLabels;
  languageSwitcher: ReactNode;
  onCreateTeam: () => void;
  onLogout: () => void | Promise<void>;
  onOpenAccountSettings: () => void;
  onSelectHome: (event: MouseEvent<HTMLAnchorElement>) => void;
  onSelectPage: (page: TopbarPageItem) => void;
  onSelectTeam: (teamId: string) => void;
  pageItems: TopbarPageItem[];
  teamItems: TopbarTeamItem[];
  userEmail?: string | null;
};
