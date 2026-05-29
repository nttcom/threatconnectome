// cspell:ignore notistack
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useDeletePTeamServiceMutation,
  useDeletePTeamServiceThumbnailMutation,
  useGetPTeamQuery,
  useGetPTeamPackagesSummaryQuery,
  useGetPTeamServiceThumbnailQuery,
  useGetSbomUploadProgressQuery,
  useUpdatePTeamServiceMutation,
  useUpdatePTeamServiceThumbnailMutation,
} from "../../../services/tcApi";
import store from "../../../store";
import { SBOMManagement } from "../SBOMManagement";
import { Status } from "../StatusPage";

const renderStatusPage = () => {
  render(
    <Provider store={store}>
      <Status />
    </Provider>,
  );
};

const renderSbomManagement = (props) => {
  render(
    <Provider store={store}>
      <SBOMManagement {...props} />
    </Provider>,
  );
};

const navigate = vi.fn();
const enqueueSnackbar = vi.fn();

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  };
});

vi.mock("notistack", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useSnackbar: vi.fn(() => ({ enqueueSnackbar })),
  };
});

vi.mock("../../../services/tcApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useGetUserMeQuery: vi.fn().mockReturnValue({
      // minimal mock for PTeamLabel
      data: {
        pteam_roles: [],
      },
      error: undefined,
      isLoading: false,
    }),
    useGetPTeamQuery: vi.fn(),
    useGetPTeamPackagesSummaryQuery: vi.fn(),
    useGetPTeamServiceThumbnailQuery: vi.fn(),
    useGetSbomUploadProgressQuery: vi.fn().mockReturnValue({
      data: [],
      error: undefined,
      isLoading: false,
      refetch: vi.fn(),
    }),
    useUpdatePTeamServiceMutation: vi.fn(),
    useDeletePTeamServiceMutation: vi.fn(),
    useUpdatePTeamServiceThumbnailMutation: vi.fn(),
    useDeletePTeamServiceThumbnailMutation: vi.fn(),
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

const testPackagesData = {
  packages: [
    {
      package_id: "685335c5-c6aa-47ed-87d9-ce1d3eeaf48d",
      package_name: "sqlparse",
      package_manager: "",
      ecosystem: "pypi",
      ssvc_priority: "out_of_cycle",
      updated_at: "2024-12-09T03:58:14.332885",
      status_count: {
        alerted: 1,
        acknowledged: 5,
        scheduled: 4,
        completed: 1,
      },
      service_ids: ["50604348-fd06-4152-afd1-2f3e73c4eb9f"],
    },
    {
      package_id: "56cfb764-e0ae-4acd-ad14-72312a30e17a",
      package_name: "setuptools",
      package_manager: "",
      ecosystem: "pypi",
      ssvc_priority: "out_of_cycle",
      updated_at: "2024-12-03T09:18:46.131242",
      status_count: {
        alerted: 2,
        acknowledged: 0,
        scheduled: 0,
        completed: 0,
      },
      service_ids: ["50604348-fd06-4152-afd1-2f3e73c4eb9f"],
    },
  ],
  ssvc_priority_count: {
    immediate: 0,
    out_of_cycle: 2,
    scheduled: 0,
    defer: 0,
  },
};

const testThumbnailDataUrl = "data:image/png;base64,test-thumbnail";

const createResolvedMutation = (resolvedValue = undefined) =>
  vi.fn(() => ({ unwrap: vi.fn().mockResolvedValue(resolvedValue) }));

describe("StatusPage", () => {
  describe("renders SBOM registration state", () => {
    beforeEach(() => {
      navigate.mockClear();
      enqueueSnackbar.mockClear();
      useGetPTeamQuery.mockClear();
      useGetPTeamPackagesSummaryQuery.mockClear();
      useGetPTeamServiceThumbnailQuery.mockClear();
      useUpdatePTeamServiceMutation.mockClear();
      useDeletePTeamServiceMutation.mockClear();
      useUpdatePTeamServiceThumbnailMutation.mockClear();
      useDeletePTeamServiceThumbnailMutation.mockClear();
      useNavigate.mockReturnValue(navigate);
      useUpdatePTeamServiceMutation.mockReturnValue([createResolvedMutation()]);
      useDeletePTeamServiceMutation.mockReturnValue([createResolvedMutation()]);
      useUpdatePTeamServiceThumbnailMutation.mockReturnValue([createResolvedMutation()]);
      useDeletePTeamServiceThumbnailMutation.mockReturnValue([createResolvedMutation()]);
      useGetPTeamServiceThumbnailQuery.mockImplementation(({ path: { service_id } }) => ({
        data: service_id === testPTeamData.services[0].service_id ? testThumbnailDataUrl : "",
        error: undefined,
        isLoading: false,
      }));
      const progresses = {
        data: [
          {
            sbom_upload_progress_id: testPTeamData["pteam_id"],
            service_name: "frontend",
            progress_rate: 0.45,
            expected_finish_time: "2026-03-17T06:24:27.776117Z",
          },
        ],
        error: false,
        isFetching: false,
      };
      useGetSbomUploadProgressQuery.mockReturnValue(progresses);
    });

    it("shows the SBOM registration state when no service is registered", () => {
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

      const packagesSummary = {
        currentData: null,
        error: false,
        isFetching: false,
      };
      useGetPTeamPackagesSummaryQuery.mockReturnValue(packagesSummary);

      renderStatusPage();
      expect(screen.getByText("Register a new SBOM")).toBeInTheDocument();
    });

    it("does not show the SBOM registration state when a service is registered", () => {
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

      const testPackagesSummary = {
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      };
      useGetPTeamPackagesSummaryQuery.mockReturnValue(testPackagesSummary);

      renderStatusPage();
      expect(screen.queryByText("Drop or click to select")).toBeNull();
    });

    it("redirects stale serviceId before loading packages summary", async () => {
      const testLocation = {
        pathname: "/",
        search: "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=old-team-service-id",
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

      renderStatusPage();

      await waitFor(() => {
        expect(navigate).toHaveBeenCalledWith(
          "/?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
        );
      });
      expect(useGetPTeamPackagesSummaryQuery).not.toHaveBeenCalled();
    });

    it("redirects missing serviceId before loading packages summary", async () => {
      const testLocation = {
        pathname: "/",
        search: "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      useGetPTeamQuery.mockReturnValue({
        data: testPTeamData,
        error: false,
        isFetching: false,
        isLoading: false,
      });

      renderStatusPage();

      await waitFor(() => {
        expect(navigate).toHaveBeenCalledWith(
          "/?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
        );
      });
      expect(useGetPTeamPackagesSummaryQuery).not.toHaveBeenCalled();
    });

    it("does not load packages summary while team data is stale", () => {
      const testLocation = {
        pathname: "/",
        search:
          "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      const testPTeam = {
        data: { ...testPTeamData, pteam_id: "previous-team-id" },
        error: false,
        isFetching: true,
        isLoading: false,
      };

      useGetPTeamQuery.mockReturnValue(testPTeam);

      renderStatusPage();

      expect(navigate).not.toHaveBeenCalled();
      expect(useGetPTeamPackagesSummaryQuery).not.toHaveBeenCalled();
    });

    it("show new SBOM registration panel when the new registration button is clicked", async () => {
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

      const testPackagesSummary = {
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      };
      useGetPTeamPackagesSummaryQuery.mockReturnValue(testPackagesSummary);

      const ue = userEvent.setup();
      renderStatusPage();

      await ue.click(screen.getByRole("button", { name: "New" }));
      expect(screen.getByText("Register a new SBOM")).toBeInTheDocument();
    });

    it("show SBOM upload progress button when the service is registered", async () => {
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

      const testPackagesSummary = {
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      };
      useGetPTeamPackagesSummaryQuery.mockReturnValue(testPackagesSummary);

      const ue = userEvent.setup();
      renderStatusPage();

      await ue.click(screen.getByLabelText("Upload Progress"));
      expect(screen.getByRole("dialog", { name: "Upload Progress" })).toBeInTheDocument();
      expect(screen.getAllByText("frontend").length).toBeGreaterThan(0);
    });

    it("keeps the image removed after saving image deletion", async () => {
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

      const testPackagesSummary = {
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      };
      useGetPTeamPackagesSummaryQuery.mockReturnValue(testPackagesSummary);

      const ue = userEvent.setup();
      renderStatusPage();

      expect(await screen.findByAltText("test_service1 image")).toBeInTheDocument();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[0]);
      await ue.click(screen.getByRole("button", { name: "Delete" }));
      await ue.click(screen.getByRole("button", { name: "Delete" }));
      await ue.click(screen.getByRole("button", { name: "Done" }));

      await waitFor(() => {
        expect(screen.queryByAltText("test_service1 image")).toBeNull();
      });
    });

    it("prevents details fields from exceeding their UI limits", async () => {
      const testLocation = {
        pathname: "/",
        search:
          "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      useGetPTeamQuery.mockReturnValue({
        data: testPTeamData,
        error: false,
        isFetching: false,
        isLoading: false,
      });

      useGetPTeamPackagesSummaryQuery.mockReturnValue({
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      });

      const ue = userEvent.setup();
      renderStatusPage();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[0]);

      const titleInput = screen.getByPlaceholderText("e.g. Payment Service SBOM");
      const validServiceName = "a".repeat(255);
      fireEvent.change(titleInput, { target: { value: validServiceName } });
      expect(titleInput).toHaveValue(validServiceName);
      fireEvent.change(titleInput, { target: { value: "a".repeat(256) } });
      expect(titleInput).toHaveValue(validServiceName);

      const descriptionInput = screen.getByPlaceholderText(
        "Enter the target system or purpose of this SBOM",
      );
      const validDescription = "b".repeat(300);
      fireEvent.change(descriptionInput, { target: { value: validDescription } });
      expect(descriptionInput).toHaveValue(validDescription);
      fireEvent.change(descriptionInput, { target: { value: "b".repeat(301) } });
      expect(descriptionInput).toHaveValue(validDescription);

      const tagsInput = screen.getByPlaceholderText("backend, prod, critical");
      const validTags = "one,two,three,four,five";
      fireEvent.change(tagsInput, { target: { value: validTags } });
      expect(tagsInput).toHaveValue(validTags);
      fireEvent.change(tagsInput, { target: { value: `${validTags},six` } });
      expect(tagsInput).toHaveValue(validTags);
      fireEvent.change(tagsInput, { target: { value: "a".repeat(21) } });
      expect(tagsInput).toHaveValue(validTags);
    });

    it("shows normalized ip addresses after saving deployments", async () => {
      const testLocation = {
        pathname: "/",
        search:
          "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      const testPTeamWithAsset = {
        ...testPTeamData,
        services: [
          {
            ...testPTeamData.services[0],
            asset: {
              ip_addresses: ["10.0.0.1"],
            },
          },
          testPTeamData.services[1],
        ],
      };

      useGetPTeamQuery.mockReturnValue({
        data: testPTeamWithAsset,
        error: false,
        isFetching: false,
        isLoading: false,
      });

      useGetPTeamPackagesSummaryQuery.mockReturnValue({
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      });

      useUpdatePTeamServiceMutation.mockReturnValue([
        createResolvedMutation({
          asset: {
            ip_addresses: ["10.0.0.1/32"],
          },
        }),
      ]);

      const ue = userEvent.setup();
      renderStatusPage();

      expect(screen.getByText("10.0.0.1")).toBeInTheDocument();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[1]);
      expect(screen.getByDisplayValue("10.0.0.1")).toBeInTheDocument();

      await ue.click(screen.getByRole("button", { name: "Done" }));

      await waitFor(() => {
        expect(screen.getByText("10.0.0.1/32")).toBeInTheDocument();
      });
    });

    it("navigate to package detail when a package row is clicked", async () => {
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

      const testPackagesSummary = {
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      };
      useGetPTeamPackagesSummaryQuery.mockReturnValue(testPackagesSummary);

      const ue = userEvent.setup();
      renderStatusPage();

      await ue.click(screen.getByText("sqlparse"));

      expect(navigate).toHaveBeenCalledWith(
        "/packages/685335c5-c6aa-47ed-87d9-ce1d3eeaf48d?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
      );
    });

    it("does not fallback to the first SBOM when initialActiveId is unknown", () => {
      renderSbomManagement({
        initialActiveId: "unknown-service-id",
        initialSboms: [
          {
            id: testPTeamData.services[0].service_id,
            title: testPTeamData.services[0].service_name,
            description: "",
            tags: [],
            imageUrl: "",
            deployments: [],
            dependencies: [],
          },
        ],
        pteamId: testPTeamData.pteam_id,
      });

      expect(screen.queryByText(testPTeamData.services[0].service_name)).toBeNull();
    });
  });
});
