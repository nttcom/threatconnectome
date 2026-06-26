import type { TopbarPageItem } from "./topbarTypes";

type IconRendererProps = {
  icon: TopbarPageItem["icon"];
  size?: number;
};

export function IconRenderer({ icon: Icon, size = 18 }: IconRendererProps) {
  return <Icon aria-hidden="true" sx={{ fontSize: size }} />;
}
