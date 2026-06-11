import { useState } from "react";

export function useTopbarMenu() {
  const [activeMenu, setActiveMenu] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);

  const close = () => {
    setActiveMenu(null);
    setAnchorEl(null);
  };

  const toggle = (menuName) => (event) => {
    if (activeMenu === menuName) {
      close();
    } else {
      setActiveMenu(menuName);
      setAnchorEl(event.currentTarget);
    }
  };

  const isOpen = (menuName) => activeMenu === menuName;

  return { anchorEl, close, toggle, isOpen };
}
