import type { Meta, StoryObj } from "@storybook/react-vite";
import { ProductEolList } from "./ProductEolListPage";

// --- ProductEolListPage のストーリー ---
const listMeta = {
  title: "Eol/ProductEolListPage",
  component: ProductEolList,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ProductEolList>;

export default listMeta;
type ListStory = StoryObj<typeof listMeta>;

// 標準表示
export const Default: ListStory = {};
