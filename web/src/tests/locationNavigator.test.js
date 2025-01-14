import { navigateSpecifiedPteam } from "../utils/locationNavigator";

test.each([
  // not navigate
  {
    locationPathname: "/",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: [{ pteam: { pteam_id: "dummyPteamId1" } }],
    navigateCallCount: 0,
    expectedParam: "",
  },
  // navigate location.pathname in status page
  {
    locationPathname: "/",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: [],
    navigateCallCount: 1,
    expectedParam: "",
  },
  // navigate location.pathname in tag page
  {
    locationPathname: "/tags/dummyTagId1",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: [],
    navigateCallCount: 1,
    expectedParam: "",
  },
  // navigate location.pathname in pteam page
  {
    locationPathname: "/pteam",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: [],
    navigateCallCount: 1,
    expectedParam: "",
  },
  // not navigate in other page
  {
    locationPathname: "/other",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: [],
    navigateCallCount: 0,
    expectedParam: "",
  },
  // navigate location.pathname and pteamId in status page
  {
    locationPathname: "/",
    locationSearch: "",
    pteamRoles: [{ pteam: { pteam_id: "pteamId1" } }],
    navigateCallCount: 1,
    expectedParam: "pteamId=pteamId1",
  },
])(
  "navigateSpecifiedPteam test",
  ({ locationPathname, locationSearch, pteamRoles, navigateCallCount, expectedParam }) => {
    const location = {
      pathname: locationPathname,
      search: locationSearch,
    };
    const mockNavigate = jest.fn();

    navigateSpecifiedPteam(location, pteamRoles, mockNavigate);

    expect(mockNavigate).toBeCalledTimes(navigateCallCount);
    if (navigateCallCount === 1) {
      const expectNavigatePath =
        expectedParam === "" ? locationPathname : locationPathname + "?" + expectedParam;
      expect(mockNavigate).toHaveBeenCalledWith(expectNavigatePath);
    }
  },
);
