import { useUploadSBOMFileMutation } from "../../../services/tcApi";
import { render, screen, waitForElementToBeRemoved } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { fireEvent } from "@testing-library/react";
import { Provider } from "react-redux";
import { SnackbarProvider, useSnackbar } from "notistack";
import { SBOMDropArea } from "../SBOMDropArea";
import store from "../../../store";

vi.mock("notistack", () => ({
  useSnackbar: vi.fn(() => ({ enqueueSnackbar: vi.fn() })),
}));

vi.mock("../../../services/tcApi", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useUploadSBOMFileMutation: vi.fn(),
  };
});

const renderSBOMDropAreaPage = () => {
  render(
    <Provider store={store}>
      <SBOMDropArea pteamId="123" onUploaded={vi.fn()} />
    </Provider>,
  );
};

describe("SBOM Upload Flow", () => {
  let enqueueSnackbar, mockUpload;

  beforeEach(() => {
    enqueueSnackbar = vi.fn();
    useSnackbar.mockReturnValue({ enqueueSnackbar });

    mockUpload = vi.fn(() => ({
      unwrap: vi.fn(() => Promise.resolve()),
    }));

    useUploadSBOMFileMutation.mockReturnValue([mockUpload]);
  });

  it("Service nameの入力とそれに伴うuploadボタンの有効化", async () => {
    renderSBOMDropAreaPage();

    const ue = userEvent.setup();
    const file = new File(["{}"], "sbom.json", { type: "application/json" });
    const dropArea = screen.getByText("Drop SBOM file here");

    fireEvent.dragOver(dropArea);
    fireEvent.drop(dropArea, {
      dataTransfer: {
        files: [file],
      },
    });

    expect(screen.getByText("Upload SBOM File")).toBeInTheDocument();

    const input = screen.getByRole("textbox", { name: /service name/i });
    await ue.type(input, "test-service");

    const uploadButton = screen.getByText("Upload");
    expect(uploadButton).not.toBeDisabled();
  });

  it("uploadボタンの押下後の動作", async () => {
    renderSBOMDropAreaPage();

    const ue = userEvent.setup();
    const file = new File(["{}"], "sbom.json", { type: "application/json" });
    const dropArea = screen.getByText("Drop SBOM file here");

    fireEvent.dragOver(dropArea);
    fireEvent.drop(dropArea, {
      dataTransfer: {
        files: [file],
      },
    });

    const input = screen.getByRole("textbox", { name: /service name/i });
    await ue.type(input, "test-service");
    await ue.click(screen.getByText("Upload"));

    await waitForElementToBeRemoved(() => screen.queryByText("Upload SBOM File"));
    expect(enqueueSnackbar).toHaveBeenCalledWith("Uploading SBOM file: sbom.json", {
      variant: "info",
    });
    expect(await screen.findByText(/Uploading SBOM file/)).toBeInTheDocument();
  });

  it("正常終了時の動作", async () => {
    const successMockUpload = vi.fn(() => ({
      unwrap: vi.fn(() => Promise.resolve({})),
    }));
    useUploadSBOMFileMutation.mockReturnValue([successMockUpload]);
    renderSBOMDropAreaPage();

    const ue = userEvent.setup();
    const file = new File(["{}"], "sbom.json", { type: "application/json" });
    const dropArea = screen.getByText("Drop SBOM file here");

    fireEvent.dragOver(dropArea);
    fireEvent.drop(dropArea, {
      dataTransfer: {
        files: [file],
      },
    });

    const input = screen.getByRole("textbox", { name: /service name/i });
    await ue.type(input, "test-service");
    await ue.click(screen.getByText("Upload"));

    expect(enqueueSnackbar).toHaveBeenCalledWith(
      "SBOM Update Request was accepted. Please reload later",
      { variant: "success" },
    );
    expect(screen.queryByText("Uploading SBOM file")).not.toBeInTheDocument();
  });

  it("異常終了時の動作", async () => {
    const errorMockUpload = vi.fn(() => ({
      unwrap: vi.fn(() => Promise.reject(new Error("Upload failed"))),
    }));
    useUploadSBOMFileMutation.mockReturnValue([errorMockUpload]);
    renderSBOMDropAreaPage();

    const ue = userEvent.setup();
    const file = new File(["{}"], "sbom.json", { type: "application/json" });
    const dropArea = screen.getByText("Drop SBOM file here");

    fireEvent.dragOver(dropArea);
    fireEvent.drop(dropArea, {
      dataTransfer: {
        files: [file],
      },
    });

    const input = screen.getByRole("textbox", { name: /service name/i });
    await ue.type(input, "test-service");
    await ue.click(screen.getByText("Upload"));

    expect(enqueueSnackbar).toHaveBeenCalledWith("Operation failed: Upload failed", {
      variant: "error",
    });
    await waitFor(() => {
      expect(screen.queryByText("Uploading SBOM file")).not.toBeInTheDocument();
    });
  });
});
