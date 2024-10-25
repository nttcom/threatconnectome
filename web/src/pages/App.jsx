import { Box } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { useDispatch, useSelector } from "react-redux";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { AppBar } from "../components/AppBar";
import { Drawer } from "../components/Drawer";
import { Main } from "../components/Main";
import { useSkipUntilAuthTokenIsReady } from "../hooks/auth";
import { useGetUserMeQuery, useTryLoginMutation } from "../services/tcApi";
import { setATeamId } from "../slices/ateam";
import { setAuthToken } from "../slices/auth";
import { setTeamMode } from "../slices/system";
import { setToken } from "../utils/api";
import { mainMaxWidth } from "../utils/const";
import { errorToString } from "../utils/func";

import { authCookieName } from "./Login";

export function App() {
  /* eslint-disable-next-line no-unused-vars */
  const [cookies, _setCookie, _removeCookie] = useCookies([authCookieName]);

  const { enqueueSnackbar } = useSnackbar();

  const skip = useSkipUntilAuthTokenIsReady();

  const dispatch = useDispatch();
  const system = useSelector((state) => state.system);
  const location = useLocation();
  const navigate = useNavigate();
  const [pteamId, setPteamId] = useState(undefined);

  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
    isFetching: userMeIsFetching,
  } = useGetUserMeQuery(undefined, { skip });
  const [tryLogin] = useTryLoginMutation();

  useEffect(() => {
    if (!skip) return; // auth token is ready
    const _checkToken = async () => {
      try {
        const accessToken = cookies[authCookieName];
        if (!accessToken) throw new Error("Missing cookie");
        dispatch(setAuthToken(accessToken));
        setToken(accessToken);
        await tryLogin().unwrap(); // throw error if accessToken is expired
      } catch (error) {
        navigate("/login", {
          state: {
            from: location.pathname,
            search: location.search,
            message: "Please login to continue.",
          },
        });
      }
    };
    _checkToken();
  }, [cookies, dispatch, location, navigate, skip, tryLogin]);

  useEffect(() => {
    if (!userMe || userMeIsFetching) return;
    const params = new URLSearchParams(location.search);
    if (["/SSVCPriority", "/analysis", "/ateam"].includes(location.pathname)) {
      dispatch(setTeamMode("ateam"));
      if (!userMe.ateams.length > 0) {
        dispatch(setATeamId(undefined));
        return;
      }
      const ateamIdx = params.get("ateamId") || userMe.ateams[0].ateam_id;
      if (!userMe.ateams.find((ateam) => ateam.ateam_id === ateamIdx)) {
        enqueueSnackbar(`Wrong ateamId. Force switching to '${userMe.ateams[0].ateam_name}'.`, {
          variant: "error",
        });
        params.set("ateamId", userMe.ateams[0].ateam_id);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
      if (params.get("ateamId") !== ateamIdx) {
        params.set("ateamId", ateamIdx);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
      dispatch(setATeamId(params.get("ateamId")));
    } else if (
      ["/", "/pteam", "/pteam/watching_request"].includes(location.pathname) ||
      /\/tags\//.test(location.pathname)
    ) {
      if (!userMe.pteams.length > 0) {
        setPteamId(undefined);
        return;
      }
      const pteamIdx = params.get("pteamId") || userMe.pteams[0].pteam_id;
      if (!userMe.pteams.find((pteam) => pteam.pteam_id === pteamIdx)) {
        enqueueSnackbar(`Wrong pteamId. Force switching to '${userMe.pteams[0].pteam_name}'.`, {
          variant: "error",
        });
        params.set("pteamId", userMe.pteams[0].pteam_id);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
      if (params.get("pteamId") !== pteamIdx) {
        params.set("pteamId", pteamIdx);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
      setPteamId(pteamIdx);
    }
  }, [dispatch, enqueueSnackbar, navigate, location, userMe, userMeIsFetching, system.teamMode]);

  if (skip) return <></>;
  if (userMeError) return <>{`Cannot get UserInfo: ${errorToString(userMeError)}`}</>;
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  return (
    <>
      <Box flexGrow={1}>
        <AppBar pteamId={pteamId} />
      </Box>
      <Drawer />
      <Main open={system.drawerOpen}>
        <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" m={1}>
          <Box display="flex" flexDirection="column" flexGrow={1} maxWidth={mainMaxWidth}>
            <Outlet />
          </Box>
        </Box>
      </Main>
    </>
  );
}
