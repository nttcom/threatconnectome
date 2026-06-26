import { colors } from "./topbarStyles";

type MarkLogoProps = {
  size?: number;
  framed?: boolean;
};

export function MarkLogo({ size = 32, framed = true }: MarkLogoProps) {
  const markGeometry = framed
    ? {
        path: "M168 164 L344 164 L268 346",
        strokeWidth: 54,
        topLeft: { cx: 168, cy: 164, r: 60 },
        topRight: { cx: 344, cy: 164, r: 60 },
        bottom: { cx: 268, cy: 346, r: 70 },
        highlightRadius: 26,
      }
    : {
        path: "M156 152 L356 152 L268 358",
        strokeWidth: 58,
        topLeft: { cx: 156, cy: 152, r: 66 },
        topRight: { cx: 356, cy: 152, r: 66 },
        bottom: { cx: 268, cy: 358, r: 76 },
        highlightRadius: 28,
      };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      fill="none"
      role="img"
      aria-label="Threatconnectome"
    >
      {framed ? (
        <>
          <rect width="512" height="512" rx="112" fill="#FFFFFF" />
          <rect
            x="22"
            y="22"
            width="468"
            height="468"
            rx="90"
            stroke={colors.slate300}
            strokeWidth="16"
          />
        </>
      ) : null}
      <path
        d={markGeometry.path}
        stroke="#0B1220"
        strokeWidth={markGeometry.strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle
        cx={markGeometry.topLeft.cx}
        cy={markGeometry.topLeft.cy}
        r={markGeometry.topLeft.r}
        fill="#0B1220"
      />
      <circle
        cx={markGeometry.topRight.cx}
        cy={markGeometry.topRight.cy}
        r={markGeometry.topRight.r}
        fill="#0B1220"
      />
      <circle
        cx={markGeometry.bottom.cx}
        cy={markGeometry.bottom.cy}
        r={markGeometry.bottom.r}
        fill="#22C55E"
      />
      <circle
        cx={markGeometry.bottom.cx}
        cy={markGeometry.bottom.cy}
        r={markGeometry.highlightRadius}
        fill="#FFFFFF"
        opacity="0.22"
      />
    </svg>
  );
}
