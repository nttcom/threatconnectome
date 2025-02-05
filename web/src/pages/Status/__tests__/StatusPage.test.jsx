import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { BrowserRouter, useLocation } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useGetPTeamQuery, useGetPTeamServiceTagsSummaryQuery } from "../../../services/tcApi";
import store from "../../../store";
import { Status } from "../StatusPage";

const renderStatusPage = () => {
  render(
    <Provider store={store}>
      <BrowserRouter>
        <Status />
      </BrowserRouter>
    </Provider>,
  );
};

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
    BrowserRouter: vi.fn().mockImplementation((props) => props.children),
  };
});

vi.mock("../../../services/tcApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useGetPTeamQuery: vi.fn(),
    useGetPTeamServiceTagsSummaryQuery: vi.fn(),
  };
});

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useSkipUntilAuthUserIsReady: vi.fn(),
  };
});

const testPTeamData = {
  pteam_id: "1d9d71ec-a341--b159-74b6d1bfffff",
  pteam_name: "test_team",
  contact_info: "",
  alert_slack: {
    enable: false,
    webhook_url: "",
  },
  alert_mail: {
    enable: false,
    address: "",
  },
  alert_ssvc_priority: "out_of_cycle",
  services: [
    {
      service_name: "test_service1",
      service_id: "50604348-fd06-4152-afd1-2f3e73c4eb9f",
      sbom_uploaded_at: null,
      description: null,
      keywords: [],
      system_exposure: "small",
      service_mission_impact: "mef_support_crippled",
      service_safety_impact: "negligible",
    },
    {
      service_name: "test_service2",
      service_id: "d36d5c85-8b37-4da2-854c-bfa58a43d83e",
      sbom_uploaded_at: "2024-10-04T07:19:25.954128",
      description: null,
      keywords: [],
      system_exposure: "open",
      service_mission_impact: "mission_failure",
      service_safety_impact: "negligible",
    },
  ],
};

const testTagsData = {
  ssvc_priority_count: {
    immediate: 0,
    out_of_cycle: 2,
    scheduled: 0,
    defer: 0,
  },
  tags: [
    {
      tag_id: "685335c5-c6aa-47ed-87d9-ce1d3eeaf48d",
      tag_name: "sqlparse:pypi:",
      parent_id: "685335c5-c6aa-47ed-87d9-ce1d3eeaf48d",
      parent_name: "sqlparse:pypi:",
      ssvc_priority: "out_of_cycle",
      updated_at: "2024-12-09T03:58:14.332885",
      status_count: {
        alerted: 1,
        acknowledged: 5,
        scheduled: 4,
        completed: 1,
      },
    },
    {
      tag_id: "56cfb764-e0ae-4acd-ad14-72312a30e17a",
      tag_name: "setuptools:pypi:",
      parent_id: "56cfb764-e0ae-4acd-ad14-72312a30e17a",
      parent_name: "setuptools:pypi:",
      ssvc_priority: "out_of_cycle",
      updated_at: "2024-12-03T09:18:46.131242",
      status_count: {
        alerted: 2,
        acknowledged: 0,
        scheduled: 0,
        completed: 0,
      },
    },
  ],
};

describe("StatusPage", () => {
  describe("renders SBOMDropArea", () => {
    it("Show SBOMDropArea component when the service is an unregistered", () => {
      const testLocation = {
        pathname: "/",
        search: "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      const _testPTeamData = { ...testPTeamData, services: [] };

      const testPTeam = {
        data: _testPTeamData,
        error: false,
        isFetching: false,
        isLoading: false,
      };

      useGetPTeamQuery.mockReturnValue(testPTeam);

      const serviceTagsSummary = {
        currentData: null,
        error: false,
        isFetching: false,
      };
      useGetPTeamServiceTagsSummaryQuery.mockReturnValue(serviceTagsSummary);

      renderStatusPage();
      expect(screen.getByText("Drop SBOM file here")).toBeInTheDocument();
    });

    it("Do not show SBOMDropArea component when the service is registered", () => {
      const testLocation = {
        pathname: "/",
        search:
          "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      const testPTeam = {
        data: testPTeamData,
        error: false,
        isFetching: false,
        isLoading: false,
      };

      useGetPTeamQuery.mockReturnValue(testPTeam);

      const testServiceTagsSummary = {
        currentData: testTagsData,
        error: false,
        isFetching: false,
      };
      useGetPTeamServiceTagsSummaryQuery.mockReturnValue(testServiceTagsSummary);

      renderStatusPage();
      expect(screen.queryByText("Drop SBOM file here")).toBeNull();
    });

    it("show SBOMDropArea component when the upload button is clicked", async () => {
      const testLocation = {
        pathname: "/",
        search:
          "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      const testPTeam = {
        data: testPTeamData,
        error: false,
        isFetching: false,
        isLoading: false,
      };

      useGetPTeamQuery.mockReturnValue(testPTeam);

      const serviceTagsSummary = {
        currentData: testTagsData,
        error: false,
        isFetching: false,
      };
      useGetPTeamServiceTagsSummaryQuery.mockReturnValue(serviceTagsSummary);

      const ue = userEvent.setup();
      renderStatusPage();

      await ue.click(screen.getByLabelText("upload button"));
      expect(screen.getByText("Drop SBOM file here")).toBeInTheDocument();
    });
  });
});
