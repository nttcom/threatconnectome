import { expect, test } from "vitest";

import { getSpecifiedPteamNavigationTarget } from "../locationNavigator";

type TestCase = {
  locationPathname: string;
  locationSearch: string;
  pteamRoles: {
    pteam_roles: Array<{ pteam: { pteam_id: string } }>;
    default_pteam_id?: string | null;
  };
  expectedTarget: string | null;
};

const cases: TestCase[] = [
  {
    locationPathname: "/",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: { pteam_roles: [{ pteam: { pteam_id: "dummyPteamId1" } }] },
    expectedTarget: null,
  },
  {
    locationPathname: "/",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: { pteam_roles: [] },
    expectedTarget: "/",
  },
  {
    locationPathname: "/package_versions/dummyPackageVersionId1",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: { pteam_roles: [] },
    expectedTarget: "/package_versions/dummyPackageVersionId1",
  },
  {
    locationPathname: "/pteam",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: { pteam_roles: [] },
    expectedTarget: "/pteam",
  },
  {
    locationPathname: "/other",
    locationSearch: "?pteamId=dummyPteamId1",
    pteamRoles: { pteam_roles: [] },
    expectedTarget: null,
  },
  {
    locationPathname: "/",
    locationSearch: "",
    pteamRoles: { pteam_roles: [{ pteam: { pteam_id: "pteamId1" } }] },
    expectedTarget: "/?pteamId=pteamId1",
  },
  {
    locationPathname: "/pteam",
    locationSearch: "?pteamId=removedPteamId",
    pteamRoles: { pteam_roles: [] },
    expectedTarget: "/pteam",
  },
  {
    locationPathname: "/pteam",
    locationSearch: "?pteamId=removedPteamId&serviceId=serviceId1",
    pteamRoles: {
      pteam_roles: [{ pteam: { pteam_id: "defaultPteamId" } }],
      default_pteam_id: "defaultPteamId",
    },
    expectedTarget: "/pteam?pteamId=defaultPteamId&serviceId=serviceId1",
  },
  {
    locationPathname: "/pteam",
    locationSearch: "?pteamId=removedPteamId",
    pteamRoles: {
      pteam_roles: [{ pteam: { pteam_id: "fallbackPteamId" } }],
      default_pteam_id: "removedPteamId",
    },
    expectedTarget: "/pteam?pteamId=fallbackPteamId",
  },
];

test.each(cases)(
  "getSpecifiedPteamNavigationTarget returns the correction target",
  ({ locationPathname, locationSearch, pteamRoles, expectedTarget }) => {
    const location = {
      pathname: locationPathname,
      search: locationSearch,
    };

    const target = getSpecifiedPteamNavigationTarget(location, pteamRoles);

    expect(target).toBe(expectedTarget);
  },
);

test("getSpecifiedPteamNavigationTarget returns null when pteam does not need correction", () => {
  const target = getSpecifiedPteamNavigationTarget(
    { pathname: "/pteam", search: "?pteamId=pteamId1" },
    { pteam_roles: [{ pteam: { pteam_id: "pteamId1" } }] },
  );

  expect(target).toBeNull();
});
