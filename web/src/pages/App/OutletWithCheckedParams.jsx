import React, { useEffect } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";
import { navigateSpecifiedPteam } from "../../utils/locationNavigator";

export function OutletWithCheckedParams() {
  const navigate = useNavigate();
  const location = useLocation();

  const skip = useSkipUntilAuthUserIsReady();

  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
    isFetching: userMeIsFetching,
  } = useGetUserMeQuery(undefined, { skip });

  useEffect(() => {
    if (!userMe || userMeIsFetching) return;
    navigateSpecifiedPteam(location, userMe.pteam_roles, navigate);
  }, [navigate, location, userMe, userMeIsFetching]);

  if (skip) return <></>;
  if (userMeError) throw new APIError(errorToString(userMeError), { api: "getUserMe" });
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  return <Outlet />;
}
