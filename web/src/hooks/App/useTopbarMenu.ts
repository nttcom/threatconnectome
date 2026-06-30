import { useState } from "react";
import type { MouseEvent } from "react";

type TopbarMenuName = "page" | "team" | "user";

export function useTopbarMenu() {
  const [activeMenu, setActiveMenu] = useState<TopbarMenuName | null>(null);
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

  const close = () => {
    setActiveMenu(null);
    setAnchorEl(null);
  };

  const toggle = (menuName: TopbarMenuName) => (event: MouseEvent<HTMLElement>) => {
    if (activeMenu === menuName) {
      close();
    } else {
      setActiveMenu(menuName);
      setAnchorEl(event.currentTarget);
    }
  };

  const isOpen = (menuName: TopbarMenuName) => activeMenu === menuName;

  return { anchorEl, close, toggle, isOpen };
}
