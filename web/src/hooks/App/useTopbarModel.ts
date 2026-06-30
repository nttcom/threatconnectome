import { useMemo, useState } from "react";
import type { MouseEvent } from "react";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth, useSkipUntilAuthUserIsReady } from "../auth";
import { tcApi, useGetUserMeQuery } from "../../services/tcApi";
import { setAuthUserIsReady, setRedirectedFrom } from "../../slices/auth";
import { buildTopbarPageUrl, getCurrentTopbarPage } from "../../utils/App/topbarNavigation";
import { preserveMyTasksParam } from "../../utils/urlUtils";
import type { UserResponse } from "../../../types/types.gen";
import type {
  TopbarLabels,
  TopbarPageItem,
  TopbarTeamItem,
} from "../../pages/App/Topbar/topbarTypes";

function buildTeamItems(
  userMe: UserResponse | undefined,
  currentTeamId: string | null,
): TopbarTeamItem[] {
  return [...(userMe?.pteam_roles ?? [])]
    .sort((a, b) => a.pteam.pteam_name.localeCompare(b.pteam.pteam_name))
    .map((role) => ({
      id: role.pteam.pteam_id,
      name: role.pteam.pteam_name,
      current: role.pteam.pteam_id === currentTeamId,
    }));
}

function getCurrentTeamId(locationSearch: string, userMe: UserResponse | undefined): string | null {
  const params = new URLSearchParams(locationSearch);
  return (
    params.get("pteamId") ??
    userMe?.default_pteam_id ??
    userMe?.pteam_roles?.[0]?.pteam?.pteam_id ??
    null
  );
}

type UseTopbarModelArgs = {
  labels: TopbarLabels;
  pageItems: TopbarPageItem[];
};

export function useTopbarModel({ labels, pageItems }: UseTopbarModelArgs) {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { signOut } = useAuth();
  const [accountSettingOpen, setAccountSettingOpen] = useState(false);
  const [teamCreationOpen, setTeamCreationOpen] = useState(false);

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });
  const hasUserMe = Boolean(userMe) && !userMeError;

  const currentPage = useMemo(
    () => getCurrentTopbarPage(location, pageItems),
    [location, pageItems],
  );
  const currentTeamId = useMemo(
    () => getCurrentTeamId(location.search, userMe),
    [location, userMe],
  );
  const teamItems = useMemo(() => buildTeamItems(userMe, currentTeamId), [userMe, currentTeamId]);
  const currentTeam = teamItems.find((item) => item.current) ?? null;

  const handleSelectPage = (page: TopbarPageItem) => {
    navigate(buildTopbarPageUrl(location.search, page));
  };

  const handleSelectHome = (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    handleSelectPage(pageItems[0]);
  };

  const handleSelectTeam = (teamId: string) => {
    if (!hasUserMe) return;
    const preservedParams = preserveMyTasksParam(location.search);
    preservedParams.set("pteamId", teamId);
    navigate("/?" + preservedParams.toString());
  };

  const handleLogout = async () => {
    dispatch(tcApi.util.resetApiState());
    dispatch(setAuthUserIsReady(false));
    dispatch(setRedirectedFrom({}));
    await signOut();
  };

  return {
    accountSettingOpen,
    currentPage,
    currentTeam,
    hasUserMe,
    labels,
    loading: skip || userMeIsLoading,
    onCreateTeam: () => setTeamCreationOpen(true),
    onLogout: handleLogout,
    onOpenAccountSettings: () => setAccountSettingOpen(true),
    onSelectHome: handleSelectHome,
    onSelectPage: handleSelectPage,
    onSelectTeam: handleSelectTeam,
    pageItems,
    setAccountSettingOpen,
    setTeamCreationOpen,
    teamCreationOpen,
    teamItems,
    userMe,
  };
}
