import { Box } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { useDispatch, useSelector } from "react-redux";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { AppBar } from "../components/AppBar";
import { Drawer } from "../components/Drawer";
import { Main } from "../components/Main";
import { setATeamId } from "../slices/ateam";
import { setAuthToken } from "../slices/auth";
import { setPTeamId } from "../slices/pteam";
import { setTeamMode } from "../slices/system";
import { getTags } from "../slices/tags";
import { getUser } from "../slices/user";
import { getMyUserInfo, setToken } from "../utils/api";
import { mainMaxWidth } from "../utils/const";

import { authCookieName } from "./Login";

export function App() {
  /* eslint-disable-next-line no-unused-vars */
  const [cookies, _setCookie, _removeCookie] = useCookies([authCookieName]);

  const [loadTags, setLoadTags] = useState(false);

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();
  const system = useSelector((state) => state.system);
  const user = useSelector((state) => state.user.user);
  const allTags = useSelector((state) => state.tags.allTags);

  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (user.user_id) return;
    const _checkToken = async () => {
      try {
        const accessToken = cookies[authCookieName];
        if (!accessToken) throw new Error("Missing cookie");
        dispatch(setAuthToken(accessToken));
        setToken(accessToken);
        await getMyUserInfo()
          .then((ret) => {
            dispatch(getUser());
          })
          .catch((err) => {
            throw err;
          });
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
  }, [cookies, dispatch, location, navigate, user]);

  useEffect(() => {
    if (!user.user_id) return;
    const params = new URLSearchParams(location.search);
    if (["/analysis", "/ateam"].includes(location.pathname)) {
      dispatch(setTeamMode("ateam"));
      if (!user.ateams.length > 0) {
        dispatch(setATeamId(undefined));
        return;
      }
      const ateamIdx = params.get("ateamId") || user.ateams[0].ateam_id;
      if (!user.ateams.find((ateam) => ateam.ateam_id === ateamIdx)) {
        enqueueSnackbar(`Wrong ateamId. Force switching to '${user.ateams[0].ateam_name}'.`, {
          variant: "error",
        });
        params.set("ateamId", user.ateams[0].ateam_id);
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
      if (!user.pteams.length > 0) {
        dispatch(setPTeamId(undefined));
        return;
      }
      const pteamIdx = params.get("pteamId") || user.pteams[0].pteam_id;
      if (!user.pteams.find((pteam) => pteam.pteam_id === pteamIdx)) {
        enqueueSnackbar(`Wrong pteamId. Force switching to '${user.pteams[0].pteam_name}'.`, {
          variant: "error",
        });
        params.set("pteamId", user.pteams[0].pteam_id);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
      if (params.get("pteamId") !== pteamIdx) {
        params.set("pteamId", pteamIdx);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
      dispatch(setPTeamId(pteamIdx));
    }
  }, [dispatch, enqueueSnackbar, navigate, location, user, system.teamMode]);

  useEffect(() => {
    if (!loadTags && allTags === undefined && user.user_id) {
      setLoadTags(true);
    }
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [user]);

  useEffect(() => {
    if (!loadTags) return;
    setLoadTags(false);
    dispatch(getTags());
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [loadTags]);

  return (
    <>
      <Box flexGrow={1}>
        <AppBar />
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
