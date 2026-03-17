import type { Meta, StoryObj } from "@storybook/react-vite";
import { http, HttpResponse } from "msw";

import { SBOMUploadProgressButton } from "./SBOMUploadProgressButton";

const pteamId = "pteam-abc-123";

const meta = {
  component: SBOMUploadProgressButton,
} satisfies Meta<typeof SBOMUploadProgressButton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Empty: Story = {
  args: { pteamId },
  parameters: {
    msw: {
      handlers: [
        http.get("*/api/pteams/*/sbom_upload_progress", () => {
          return HttpResponse.json([]);
        }),
      ],
    },
  },
};

export const Single: Story = {
  args: { pteamId },
  parameters: {
    msw: {
      handlers: [
        http.get("*/api/pteams/*/sbom_upload_progress", () => {
          return HttpResponse.json([
            {
              sbom_upload_progress_id: "123e4567-e89b-12d3-a456-426614174000",
              service_name: "frontend",
              progress_rate: 0.45,
              expected_finish_time: "2026-03-17T06:24:27.776117Z",
            },
          ]);
        }),
      ],
    },
  },
};

export const Multiple: Story = {
  args: { pteamId },
  parameters: {
    msw: {
      handlers: [
        http.get("*/api/pteams/*/sbom_upload_progress", () => {
          return HttpResponse.json([
            {
              sbom_upload_progress_id: "123e4567-e89b-12d3-a456-426614174000",
              service_name: "frontend",
              progress_rate: 0.45,
              expected_finish_time: "2026-03-17T06:24:27.776117Z",
            },
            {
              sbom_upload_progress_id: "123e4567-e89b-12d3-a456-426614174000",
              service_name: "backend",
              progress_rate: 0.8,
              expected_finish_time: "2026-03-17T06:24:27.776117Z",
            },
            {
              sbom_upload_progress_id: "123e4567-e89b-12d3-a456-426614174000",
              service_name: "mobile-app",
              progress_rate: 0.1,
              expected_finish_time: "2026-03-17T06:24:27.776117Z",
            },
          ]);
        }),
      ],
    },
  },
};

export const LongSingleWord: Story = {
  args: { pteamId },
  parameters: {
    msw: {
      handlers: [
        http.get("*/api/pteams/*/sbom_upload_progress", () => {
          return HttpResponse.json([
            {
              sbom_upload_progress_id: "123e4567-e89b-12d3-a456-426614174000",
              service_name:
                // cspell:disable-next-line
                "averylongservicenamethathasnospacesordashesandshouldoverflowthecontainerandkeepgoingwellbeyondanynormalservicenamelength",
              progress_rate: 0.45,
              expected_finish_time: "2026-03-17T06:24:27.776117Z",
            },
          ]);
        }),
      ],
    },
  },
};
