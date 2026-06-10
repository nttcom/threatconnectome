import { useMemo, useState } from "react";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth, useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { tcApi, useGetUserMeQuery } from "../../services/tcApi";
import { setAuthUserIsReady, setRedirectedFrom } from "../../slices/auth";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import { preserveMyTasksParam } from "../../utils/urlUtils";

import { buildTopbarPageUrl, getCurrentTopbarPage } from "./topbarNavigation";

function buildTeamItems(userMe, currentTeamId) {
  return [...(userMe?.pteam_roles ?? [])]
    .sort((a, b) => a.pteam.pteam_name.localeCompare(b.pteam.pteam_name))
    .map((role) => ({
      id: role.pteam.pteam_id,
      name: role.pteam.pteam_name,
      current: role.pteam.pteam_id === currentTeamId,
    }));
}

function getCurrentTeamId(locationSearch, userMe) {
  const params = new URLSearchParams(locationSearch);
  return (
    params.get("pteamId") ??
    userMe?.default_pteam_id ??
    userMe?.pteam_roles?.[0]?.pteam?.pteam_id ??
    null
  );
}

export function useTopbarModel({ labels, pageItems }) {
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

  if (userMeError) {
    throw new APIError(errorToString(userMeError), { api: "getUserMe" });
  }

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

  const handleSelectPage = (page) => {
    navigate(buildTopbarPageUrl(location.search, page));
  };

  const handleSelectHome = (event) => {
    event.preventDefault();
    handleSelectPage(pageItems[0]);
  };

  const handleSelectTeam = (teamId) => {
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
