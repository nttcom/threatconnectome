import type { Meta, StoryObj } from "@storybook/react-vite";
import { http, HttpResponse } from "msw";

import generalEoLData from "../../mocks/generalEoLData.json";

import { ProductEolList } from "./ProductEolListPage";

// --- ProductEolListPage story ---
const listMeta = {
  title: "Eol/ProductEolListPage",
  component: ProductEolList,
  parameters: {
    layout: "fullscreen",
    msw: {
      handlers: [
        http.get("*/eols", () => {
          return HttpResponse.json(generalEoLData);
        }),
      ],
    },
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ProductEolList>;

export default listMeta;
type ListStory = StoryObj<typeof listMeta>;

export const Default: ListStory = {};
