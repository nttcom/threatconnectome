import { Alert, Box } from "@mui/material";
import { useSnackbar } from "notistack";
import React, { useEffect, useState } from "react";
import { useCookies } from "react-cookie";
import { useDispatch, useSelector } from "react-redux";
import { Outlet, useLocation, useNavigate } from "react-router-dom";

import { AppBar } from "../components/AppBar";
import { Drawer } from "../components/Drawer";
import { Main } from "../components/Main";
import { setATeamId } from "../slices/ateam";
import { setGTeamId } from "../slices/gteam";
import { getPTeamTagsSummary, setPTeamId } from "../slices/pteam";
import { setTeamMode } from "../slices/system";
import { getTags } from "../slices/tags";
import { getUser } from "../slices/user";
import { getMyUserInfo, setToken } from "../utils/api";
import { mainMaxWidth, threatImpactName, threatImpactProps } from "../utils/const";

import { authCookieName } from "./Login";

export function App() {
  /* eslint-disable-next-line no-unused-vars */
  const [cookies, _setCookie, _removeCookie] = useCookies([authCookieName]);

  const [loadTags, setLoadTags] = useState(false);
  const [loadSummary, setLoadSummary] = useState(false);
  const [prevPTeamId, setPrevPTeamId] = useState(undefined);
  const [prevSummary, setPrevSummary] = useState(undefined);

  const { enqueueSnackbar } = useSnackbar();

  const dispatch = useDispatch();
  const system = useSelector((state) => state.system);
  const user = useSelector((state) => state.user.user);
  const allTags = useSelector((state) => state.tags.allTags);
  const pteamId = useSelector((state) => state.pteam.pteamId);
  const summary = useSelector((state) => state.pteam.tagsSummary);

  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (user.user_id) return;
    const _checkToken = async () => {
      try {
        if (!cookies[authCookieName]) throw new Error("Missing cookie");
        setToken(cookies[authCookieName]);
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
    } else if (["/gteam"].includes(location.pathname) || /\/zone/.test(location.pathname)) {
      dispatch(setTeamMode("gteam"));
      if (!user.gteams.length > 0) {
        dispatch(setGTeamId(undefined));
        return;
      }
      const gteamIdx = params.get("gteamId") || user.gteams[0].gteam_id;
      if (!user.gteams.find((gteam) => gteam.gteam_id === gteamIdx)) {
        enqueueSnackbar(`Wrong gteamId. Force switching to '${user.gteams[0].gteam_name}'.`, {
          variant: "error",
        });
        params.set("gteamId", user.gteams[0].gteam_id);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
      if (params.get("gteamId") !== gteamIdx) {
        params.set("gteamId", gteamIdx);
        navigate(location.pathname + "?" + params.toString());
        return;
      }
      dispatch(setGTeamId(params.get("gteamId")));
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

  useEffect(() => {
    if (!pteamId) return;
    if (pteamId !== prevPTeamId) {
      setPrevSummary(undefined);
      setPrevPTeamId(pteamId);
    }
    if (loadSummary) {
      setPrevSummary(summary);
      dispatch(getPTeamTagsSummary(pteamId));
      setLoadSummary(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatch, loadSummary, pteamId]);

  const getWorst = (threatImpactCounts) =>
    parseInt(Object.keys(threatImpactCounts).filter((key) => threatImpactCounts[key] > 0)[0] ?? 4);
  const getThreatProp = (num) => threatImpactProps[threatImpactName[parseInt(num)]];

  useEffect(() => {
    if (!summary) setLoadSummary(true);
    if (!pteamId || !prevPTeamId || pteamId !== prevPTeamId) return;
    if (summary && prevSummary && summary !== prevSummary) {
      const newThreatImpact = getWorst(summary.threat_impact_count ?? []);
      const prevThreatImpact = getWorst(prevSummary.threat_impact_count ?? []);
      if (newThreatImpact !== prevThreatImpact) {
        enqueueSnackbar(
          "Your pteam's Threat Impact got " +
            (newThreatImpact > prevThreatImpact ? "better" : "worse") +
            " to " +
            getThreatProp(newThreatImpact).chipLabel,
          { variant: newThreatImpact > prevThreatImpact ? "info" : "warning" }
        );
      }
    }
    setPrevSummary(summary);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatch, summary]);

  return (
    <>
      <Box flexGrow={1}>
        <AppBar />
      </Box>
      <Drawer />
      <Main open={system.drawerOpen}>
        <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" m={1}>
          <Box display="flex" flexDirection="column" flexGrow={1} maxWidth={mainMaxWidth}>
            {summary && summary.threat_impact_count?.["1"] > 0 && (
              <Box sx={{ width: 1 }} mb={3}>
                <Alert severity="error">{threatImpactProps.immediate.alert}</Alert>
              </Box>
            )}
            <Outlet />
          </Box>
        </Box>
      </Main>
    </>
  );
}
