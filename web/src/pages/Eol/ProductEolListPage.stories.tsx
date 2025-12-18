import type { Meta, StoryObj } from "@storybook/react-vite";
import { ProductEolListPage } from "./ProductEolPage";

// --- ProductEolListPage のストーリー ---
const listMeta = {
  title: "Eol/ProductEolListPage",
  component: ProductEolListPage,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ProductEolListPage>;

export default listMeta;
type ListStory = StoryObj<typeof listMeta>;

// 標準表示
export const Default: ListStory = {};
