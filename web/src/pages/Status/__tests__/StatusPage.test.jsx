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
import { normalizeServiceImageToPng } from "../../../utils/serviceImageUtils";
import { SBOMManagement } from "../SBOMManagement/SBOMManagement";
import { Status } from "../StatusPage";

const renderStatusPage = () => {
  return render(
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

vi.mock("../../../utils/serviceImageUtils", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    normalizeServiceImageToPng: vi.fn(),
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
let queryPTeamData;
let queryThumbnailByServiceId;
let queryThumbnailErrorByServiceId;
let queryThumbnailFetchingByServiceId;

const createResolvedMutation = (resolvedValue = undefined, onResolve) =>
  vi.fn(() => ({
    unwrap: vi.fn().mockImplementation(async () => {
      onResolve?.();
      return resolvedValue;
    }),
  }));

const createRejectedMutation = (rejectedValue) =>
  vi.fn(() => ({ unwrap: vi.fn().mockRejectedValue(rejectedValue) }));

const updateServiceInPTeamData = (serviceId, patch) => {
  queryPTeamData = {
    ...queryPTeamData,
    services: queryPTeamData.services.map((service) =>
      service.service_id === serviceId ? { ...service, ...patch } : service,
    ),
  };
};

const updateServiceAssetInPTeamData = (serviceId, ipAddresses) => {
  queryPTeamData = {
    ...queryPTeamData,
    services: queryPTeamData.services.map((service) =>
      service.service_id === serviceId
        ? {
            ...service,
            asset: {
              ...service.asset,
              ip_addresses: ipAddresses,
            },
          }
        : service,
    ),
  };
};

describe("StatusPage", () => {
  describe("renders SBOM registration state", () => {
    beforeEach(() => {
      queryPTeamData = structuredClone(testPTeamData);
      queryThumbnailByServiceId = {
        [testPTeamData.services[0].service_id]: testThumbnailDataUrl,
        [testPTeamData.services[1].service_id]: "",
      };
      queryThumbnailErrorByServiceId = {
        [testPTeamData.services[0].service_id]: undefined,
        [testPTeamData.services[1].service_id]: undefined,
      };
      queryThumbnailFetchingByServiceId = {
        [testPTeamData.services[0].service_id]: false,
        [testPTeamData.services[1].service_id]: false,
      };
      navigate.mockClear();
      enqueueSnackbar.mockClear();
      useGetPTeamQuery.mockClear();
      useGetPTeamPackagesSummaryQuery.mockClear();
      useGetPTeamServiceThumbnailQuery.mockClear();
      useUpdatePTeamServiceMutation.mockClear();
      useDeletePTeamServiceMutation.mockClear();
      useUpdatePTeamServiceThumbnailMutation.mockClear();
      useDeletePTeamServiceThumbnailMutation.mockClear();
      normalizeServiceImageToPng.mockReset();
      useNavigate.mockReturnValue(navigate);
      useUpdatePTeamServiceMutation.mockReturnValue([createResolvedMutation()]);
      useDeletePTeamServiceMutation.mockReturnValue([createResolvedMutation()]);
      useUpdatePTeamServiceThumbnailMutation.mockReturnValue([createResolvedMutation()]);
      useDeletePTeamServiceThumbnailMutation.mockReturnValue([createResolvedMutation()]);
      normalizeServiceImageToPng.mockResolvedValue({
        file: new File(["test"], "test.png", { type: "image/png" }),
        previewDataUrl: "data:image/png;base64,test-preview",
      });
      useGetPTeamServiceThumbnailQuery.mockImplementation(({ path: { service_id } }) => ({
        data: queryThumbnailByServiceId[service_id] ?? "",
        error: queryThumbnailErrorByServiceId[service_id],
        isFetching: queryThumbnailFetchingByServiceId[service_id] ?? false,
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
      expect(screen.getByText("Details")).toBeInTheDocument();
      expect(screen.getByText("Deployments")).toBeInTheDocument();
      expect(screen.getByText("Danger Zone")).toBeInTheDocument();
    });

    it("shows the numeric row count in the dependencies page-size selector", () => {
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

      renderStatusPage();

      const pageSizeSelector = screen.getByRole("combobox");

      expect(screen.getByText("Rows")).toBeInTheDocument();
      expect(pageSizeSelector).toHaveTextContent("10");
      expect(pageSizeSelector).not.toHaveTextContent("countItems");
    });

    it("copies the service id from the details title action", async () => {
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

      const writeText = vi.fn().mockResolvedValue(undefined);
      Object.defineProperty(window.navigator, "clipboard", {
        configurable: true,
        value: { writeText },
      });

      renderStatusPage();

      fireEvent.click(screen.getByRole("button", { name: "Copy service ID" }));

      await waitFor(() => {
        expect(writeText).toHaveBeenCalledWith(testPTeamData.services[0].service_id);
      });
    });

    it("shows system exposure and mission impact from the service API", () => {
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

      renderStatusPage();

      expect(screen.getByText("Small")).toBeInTheDocument();
      expect(screen.getByText("MEF Support Crippled")).toBeInTheDocument();
    });

    it("navigates when a different SBOM tab is selected", async () => {
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
      const renderResult = renderStatusPage();

      await ue.click(screen.getByRole("button", { name: "test_service2" }));

      expect(navigate).toHaveBeenCalledWith(
        "/?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=d36d5c85-8b37-4da2-854c-bfa58a43d83e",
      );
    });

    it("discards unsaved details draft when a different SBOM tab is selected", async () => {
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
      fireEvent.change(screen.getByPlaceholderText("e.g. Payment Service SBOM"), {
        target: { value: "unsaved service title" },
      });

      await ue.click(screen.getByRole("button", { name: "test_service2" }));

      expect(navigate).toHaveBeenCalledWith(
        "/?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=d36d5c85-8b37-4da2-854c-bfa58a43d83e",
      );
      expect(screen.queryByRole("button", { name: "unsaved service title" })).toBeNull();
      expect(screen.getByRole("button", { name: "test_service1" })).toBeInTheDocument();
    });

    it("updates system exposure and mission impact through the service API", async () => {
      const testLocation = {
        pathname: "/",
        search:
          "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      useGetPTeamQuery.mockImplementation(() => ({
        data: queryPTeamData,
        error: false,
        isFetching: false,
        isLoading: false,
      }));

      useGetPTeamPackagesSummaryQuery.mockReturnValue({
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      });

      const updateService = createResolvedMutation(
        {
          system_exposure: "controlled-from-response",
          service_mission_impact: "degraded",
        },
        () => {
          updateServiceInPTeamData(testPTeamData.services[0].service_id, {
            system_exposure: "open",
            service_mission_impact: "mission_failure",
          });
        },
      );
      useUpdatePTeamServiceMutation.mockReturnValue([updateService]);

      const ue = userEvent.setup();
      const renderResult = renderStatusPage();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[1]);
      await ue.click(screen.getByRole("button", { name: /Open/ }));
      await ue.click(screen.getByRole("button", { name: /Mission Failure/ }));
      await ue.click(screen.getByRole("button", { name: "Done" }));

      await waitFor(() => {
        expect(updateService).toHaveBeenCalledWith({
          path: {
            pteam_id: testPTeamData.pteam_id,
            service_id: testPTeamData.services[0].service_id,
          },
          body: {
            system_exposure: "open",
            service_mission_impact: "mission_failure",
          },
        });
      });
      expect(screen.getByText("Small")).toBeInTheDocument();
      expect(screen.getByText("MEF Support Crippled")).toBeInTheDocument();
      expect(screen.queryByText("Degraded")).toBeNull();
      renderResult.rerender(
        <Provider store={store}>
          <Status />
        </Provider>,
      );
      expect(enqueueSnackbar).toHaveBeenCalledWith("Risk settings updated", {
        variant: "success",
      });
      expect(screen.queryByRole("button", { name: "Done" })).toBeNull();
      expect(screen.getByText("Open")).toBeInTheDocument();
      expect(screen.getByText("Mission Failure")).toBeInTheDocument();
    });

    it("keeps risk settings editable when the update fails", async () => {
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

      const updateService = createRejectedMutation({
        status: 400,
        data: { detail: "boom" },
      });
      useUpdatePTeamServiceMutation.mockReturnValue([updateService]);

      const ue = userEvent.setup();
      const renderResult = renderStatusPage();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[1]);
      await ue.click(screen.getByRole("button", { name: /Open/ }));
      await ue.click(screen.getByRole("button", { name: "Done" }));

      await waitFor(() => {
        expect(updateService).toHaveBeenCalled();
      });
      expect(enqueueSnackbar).toHaveBeenCalledWith("Update failed: 400: boom", {
        variant: "error",
      });
      expect(screen.getByRole("button", { name: "Done" })).toBeInTheDocument();
    });

    it("keeps the tab title on the last fetched service name when details save fails", async () => {
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

      useUpdatePTeamServiceMutation.mockReturnValue([
        createRejectedMutation({
          status: 400,
          data: { detail: "boom" },
        }),
      ]);

      const ue = userEvent.setup();
      renderStatusPage();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[0]);
      const titleInput = screen.getByPlaceholderText("e.g. Payment Service SBOM");
      fireEvent.change(titleInput, { target: { value: "Updated service name" } });

      await ue.click(screen.getByRole("button", { name: "Done" }));

      await waitFor(() => {
        expect(enqueueSnackbar).toHaveBeenCalledWith("Update failed: 400: boom", {
          variant: "error",
        });
      });

      expect(screen.getByRole("button", { name: "test_service1" })).toBeInTheDocument();
    });

    it("blocks saving details when the trimmed service name is empty", async () => {
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

      const updateService = createResolvedMutation();
      useUpdatePTeamServiceMutation.mockReturnValue([updateService]);

      const ue = userEvent.setup();
      renderStatusPage();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[0]);
      const titleInput = screen.getByPlaceholderText("e.g. Payment Service SBOM");
      fireEvent.change(titleInput, { target: { value: "   " } });

      expect(screen.getByRole("button", { name: "Done" })).toBeDisabled();
      expect(screen.getByText("Service name cannot be empty.")).toBeInTheDocument();

      await ue.click(screen.getByRole("button", { name: "Done" }));

      expect(updateService).not.toHaveBeenCalled();
    });

    it("shows refreshed service details after saving them", async () => {
      const testLocation = {
        pathname: "/",
        search:
          "?pteamId=1d9d71ec-a341--b159-74b6d1bfffff&serviceId=50604348-fd06-4152-afd1-2f3e73c4eb9f",
      };
      useLocation.mockReturnValue(testLocation);
      useSkipUntilAuthUserIsReady.mockReturnValue(false);

      useGetPTeamQuery.mockImplementation(() => ({
        data: queryPTeamData,
        error: false,
        isFetching: false,
        isLoading: false,
      }));

      useGetPTeamPackagesSummaryQuery.mockReturnValue({
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      });

      const updateService = createResolvedMutation(
        {
          service_name: "response service name",
          description: "response description",
          keywords: ["response"],
        },
        () => {
          updateServiceInPTeamData(testPTeamData.services[0].service_id, {
            service_name: "Payment Service SBOM V2",
            description: "Updated service description",
            keywords: ["backend", "critical", "prod"],
          });
        },
      );
      useUpdatePTeamServiceMutation.mockReturnValue([updateService]);

      const ue = userEvent.setup();
      const renderResult = renderStatusPage();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[0]);

      const titleInput = screen.getByPlaceholderText("e.g. Payment Service SBOM");
      fireEvent.change(titleInput, { target: { value: "Payment Service SBOM V2" } });

      const descriptionInput = screen.getByPlaceholderText(
        "Enter the target system or purpose of this service",
      );
      fireEvent.change(descriptionInput, {
        target: { value: "Updated service description" },
      });

      const tagsInput = screen.getByPlaceholderText("backend, prod, critical");
      fireEvent.change(tagsInput, { target: { value: "backend, prod, critical" } });

      await ue.click(screen.getByRole("button", { name: "Done" }));

      expect(screen.getByRole("button", { name: "test_service1" })).toBeInTheDocument();
      expect(screen.queryByText("response description")).toBeNull();
      expect(screen.queryByText("response")).toBeNull();
      expect(screen.queryByText("Updated service description")).toBeNull();

      renderResult.rerender(
        <Provider store={store}>
          <Status />
        </Provider>,
      );

      await waitFor(() => {
        expect(screen.getByText("Updated service description")).toBeInTheDocument();
      });
      expect(screen.getByText("Updated service description")).toBeInTheDocument();
      expect(screen.getByText("backend")).toBeInTheDocument();
      expect(screen.getByText("critical")).toBeInTheDocument();
      expect(screen.getByText("prod")).toBeInTheDocument();
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
      const renderResult = renderStatusPage();

      await ue.click(screen.getByRole("button", { name: "New" }));
      expect(screen.getByText("Register a new SBOM")).toBeInTheDocument();

      const uploadButton = screen.getByText("Upload an SBOM").closest("button");
      expect(uploadButton).not.toBeNull();
      await ue.click(uploadButton);
      expect(screen.getByRole("dialog")).toBeInTheDocument();
      expect(screen.getByText("Upload SBOM")).toBeInTheDocument();
      expect(screen.getByText("Drop or click to select")).toBeInTheDocument();
    });

    it("opens the upload dialog with warning text when the SBOM update button is clicked", async () => {
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

      useGetPTeamServiceThumbnailQuery.mockReturnValue({
        data: testThumbnailDataUrl,
        error: false,
        isFetching: false,
      });

      const ue = userEvent.setup();
      renderStatusPage();

      await ue.click(screen.getByRole("button", { name: "Update SBOM" }));
      expect(screen.getByRole("dialog")).toBeInTheDocument();
      expect(screen.getByText("Upload SBOM")).toBeInTheDocument();
      expect(
        screen.getByText(
          "Important: Uploading an incorrect SBOM may delete related tickets. Please ensure the SBOM is correct before uploading.",
        ),
      ).toBeInTheDocument();
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
      const renderResult = renderStatusPage();

      await ue.click(screen.getByLabelText("Upload Progress"));
      expect(screen.getByRole("dialog", { name: "Upload Progress" })).toBeInTheDocument();
      expect(screen.getAllByText("frontend").length).toBeGreaterThan(0);
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
      const renderResult = renderStatusPage();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[0]);

      const titleInput = screen.getByPlaceholderText("e.g. Payment Service SBOM");
      const validServiceName = "a".repeat(255);
      fireEvent.change(titleInput, { target: { value: validServiceName } });
      expect(titleInput).toHaveValue(validServiceName);
      fireEvent.change(titleInput, { target: { value: "a".repeat(256) } });
      expect(titleInput).toHaveValue(validServiceName);

      const descriptionInput = screen.getByPlaceholderText(
        "Enter the target system or purpose of this service",
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

      queryPTeamData = structuredClone(testPTeamWithAsset);
      useGetPTeamQuery.mockImplementation(() => ({
        data: queryPTeamData,
        error: false,
        isFetching: false,
        isLoading: false,
      }));

      useGetPTeamPackagesSummaryQuery.mockReturnValue({
        currentData: testPackagesData,
        error: false,
        isFetching: false,
      });

      useUpdatePTeamServiceMutation.mockReturnValue([
        createResolvedMutation(
          {
            asset: {
              ip_addresses: ["response-ip"],
            },
          },
          () =>
            updateServiceAssetInPTeamData(testPTeamData.services[0].service_id, ["10.0.0.1/32"]),
        ),
      ]);

      const ue = userEvent.setup();
      const renderResult = renderStatusPage();

      expect(screen.getByText("10.0.0.1")).toBeInTheDocument();

      await ue.click(screen.getAllByRole("button", { name: "Edit" })[2]);
      expect(screen.getByDisplayValue("10.0.0.1")).toBeInTheDocument();

      await ue.click(screen.getByRole("button", { name: "Done" }));

      expect(screen.getByText("10.0.0.1")).toBeInTheDocument();
      expect(screen.queryByText("response-ip")).toBeNull();
      expect(screen.queryByText("10.0.0.1/32")).toBeNull();

      renderResult.rerender(
        <Provider store={store}>
          <Status />
        </Provider>,
      );

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

    it("uses currentService.id as the active SBOM", () => {
      renderSbomManagement({
        currentDependencies: [],
        currentService: {
          id: testPTeamData.services[0].service_id,
          title: testPTeamData.services[0].service_name,
          description: "",
          tags: [],
          systemExposure: "small",
          missionImpact: "mef_support_crippled",
          imageUrl: "",
          deployments: [],
        },
        pteamId: testPTeamData.pteam_id,
        serviceTabs: [
          {
            id: testPTeamData.services[0].service_id,
            title: testPTeamData.services[0].service_name,
          },
        ],
      });

      expect(screen.getByText("Small")).toBeInTheDocument();
      expect(screen.getByText("MEF Support Crippled")).toBeInTheDocument();
      expect(screen.queryByText("Register a new SBOM")).toBeNull();
    });

    it("keeps the tab UI visible while the selected service details are unresolved", async () => {
      const onActiveIdChange = vi.fn();
      const ue = userEvent.setup();

      renderSbomManagement({
        currentDependencies: [],
        currentService: {
          id: testPTeamData.services[0].service_id,
          title: testPTeamData.services[0].service_name,
          description: "",
          tags: [],
          systemExposure: "small",
          missionImpact: "mef_support_crippled",
          imageUrl: "",
          deployments: [],
        },
        onActiveIdChange,
        pteamId: testPTeamData.pteam_id,
        serviceTabs: [
          {
            id: testPTeamData.services[0].service_id,
            title: testPTeamData.services[0].service_name,
          },
          {
            id: testPTeamData.services[1].service_id,
            title: testPTeamData.services[1].service_name,
          },
        ],
      });

      await ue.click(screen.getByRole("button", { name: "test_service2" }));

      expect(onActiveIdChange).toHaveBeenCalledWith(testPTeamData.services[1].service_id);
      expect(screen.getByRole("button", { name: "test_service1" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "test_service2" })).toBeInTheDocument();
      expect(screen.getByText("Loading selected SBOM...")).toBeInTheDocument();
    });
  });
});
