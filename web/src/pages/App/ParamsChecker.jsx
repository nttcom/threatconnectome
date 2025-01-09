import { useSnackbar } from "notistack";
import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthTokenIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { LocationReader } from "../../utils/LocationReader";
import { errorToString } from "../../utils/func";

export function ParamsChecker() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { enqueueSnackbar } = useSnackbar();

  const skip = useSkipUntilAuthTokenIsReady();

  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
    isFetching: userMeIsFetching,
  } = useGetUserMeQuery(undefined, { skip });

  useEffect(() => {
    if (!userMe || userMeIsFetching) return;
    const params = new URLSearchParams(location.search);
    const locationReader = new LocationReader(location);
    if (
      locationReader.isStatusPage() ||
      locationReader.isTagPage() ||
      locationReader.isPTeamPage()
    ) {
      if (!userMe.pteam_roles.length > 0) {
        if (params.get("pteamId")) {
          navigate(location.pathname);
        }
        return;
      }
      const pteamIdx = params.get("pteamId") || userMe.pteam_roles[0].pteam.pteam_id;
      if (params.get("pteamId") !== pteamIdx) {
        params.set("pteamId", pteamIdx);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
    }
  }, [dispatch, enqueueSnackbar, navigate, location, userMe, userMeIsFetching]);

  if (skip) return <></>;
  if (userMeError) throw new APIError(errorToString(userMeError), { api: "getUserMe" });
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  return <Outlet />;
}
