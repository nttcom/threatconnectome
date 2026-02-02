// モバイル表示用カードのモックデータ

export type Status = "expired" | "warning" | "active" | "unknown";

type EolCardItem = {
  id: string;
  status: Status;
  productName: string;
  version: string;
  category: string;
  eolDate: string | null;
  diffText: string;
  services: { id: string; name: string }[];
};

export const mockEolCardData: EolCardItem[] = [
  {
    id: "1",
    status: "expired",
    productName: "Python",
    version: "3.8",
    category: "Language",
    eolDate: "2024-10-14",
    diffText: "120 days over",
    services: [
      { id: "s1", name: "api-service" },
      { id: "s2", name: "batch-processor" },
    ],
  },
  {
    id: "2",
    status: "warning",
    productName: "Node.js",
    version: "18.x",
    category: "Framework",
    eolDate: "2025-04-30",
    diffText: "90 days over",
    services: [{ id: "s3", name: "frontend" }],
  },
  {
    id: "3",
    status: "active",
    productName: "PostgreSQL",
    version: "16",
    category: "Database",
    eolDate: "2028-11-09",
    diffText: "1380 days over",
    services: [
      { id: "s4", name: "database-service" },
      { id: "s5", name: "analytics-service" },
    ],
  },
  // エッジケース
  {
    id: "4",
    status: "unknown",
    productName: "lodash",
    version: "4.17.21",
    category: "Library",
    eolDate: null,
    diffText: "-",
    services: [{ id: "s6", name: "utils-service" }],
  },
  {
    id: "5",
    status: "expired",
    productName: "Java",
    version: "11",
    category: "Runtime",
    eolDate: "2026-01-28",
    diffText: "Expires today",
    services: [{ id: "s7", name: "legacy-api" }],
  },
  {
    id: "6",
    status: "active",
    productName: "@angular-devkit/build-angular-with-extra-long-package-name",
    version: "17.0.0-rc.4",
    category: "Framework",
    eolDate: "2027-05-15",
    diffText: "850 days left",
    services: [{ id: "s8", name: "legacy-api" }],
  },
  {
    id: "7",
    status: "warning",
    productName: "Redis",
    version: "6.2",
    category: "Database",
    eolDate: "2025-06-01",
    diffText: "120 days left",
    services: [
      { id: "s9", name: "legacy-api" },
      { id: "s10", name: "session-store" },
      { id: "s11", name: "queue-backend" },
      { id: "s12", name: "rate-limiter" },
      { id: "s13", name: "pub-sub-broker" },
      { id: "s14", name: "realtime-notifications" },
    ],
  },
  {
    id: "8",
    status: "active",
    productName: "Docker",
    version: "24.0",
    category: "Tool",
    eolDate: "2029-12-31",
    diffText: "1500 days left",
    services: [],
  },
];
