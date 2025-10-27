import { useEffect, useState } from "react";

export function useViewportOffset() {
  const [offsetTop, setOffsetTop] = useState(0);

  useEffect(() => {
    if (typeof window === "undefined" || !window.visualViewport) return;

    const vv = window.visualViewport;

    const handleViewportChange = () => {
      setOffsetTop(vv.offsetTop || 0);
    };

    handleViewportChange();

    vv.addEventListener("resize", handleViewportChange);
    vv.addEventListener("scroll", handleViewportChange);

    return () => {
      vv.removeEventListener("resize", handleViewportChange);
      vv.removeEventListener("scroll", handleViewportChange);
    };
  }, []);

  return offsetTop;
}
