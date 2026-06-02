import { act, render } from "@testing-library/react";

import { useSBOMManagementState } from "../useSBOMManagementState";

let latestState;

function StateHarness(props) {
  latestState = useSBOMManagementState(props);
  return null;
}

describe("useSBOMManagementState", () => {
  it("exposes the thumbnail edit state API and clears the override after refetch", () => {
    const baseProps = {
      currentDependencies: [],
      currentService: null,
      isThumbnailFetching: false,
      serviceTabs: [],
    };

    const { rerender } = render(<StateHarness {...baseProps} />);

    expect(typeof latestState.setPendingThumbnail).toBe("function");
    expect(typeof latestState.setThumbnailDisplayOverride).toBe("function");
    expect(typeof latestState.setAwaitingThumbnailRefresh).toBe("function");
    expect(typeof latestState.markClean).toBe("function");

    act(() => {
      latestState.setPendingThumbnail({
        deleted: false,
        file: null,
        previewDataUrl: "data:image/png;base64,preview",
      });
      latestState.setThumbnailDisplayOverride("data:image/png;base64,override");
      latestState.setAwaitingThumbnailRefresh(true);
    });

    expect(latestState.pendingThumbnail).toEqual({
      deleted: false,
      file: null,
      previewDataUrl: "data:image/png;base64,preview",
    });
    expect(latestState.thumbnailDisplayOverride).toBe("data:image/png;base64,override");
    expect(latestState.awaitingThumbnailRefresh).toBe(true);

    act(() => {
      rerender(<StateHarness {...baseProps} isThumbnailFetching />);
    });

    act(() => {
      rerender(<StateHarness {...baseProps} />);
    });

    expect(latestState.thumbnailDisplayOverride).toBeNull();
    expect(latestState.awaitingThumbnailRefresh).toBe(false);
  });
});
