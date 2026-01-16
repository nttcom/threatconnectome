// EOL管理ダッシュボード用モックデータ

// カテゴリ定数
export const CATEGORIES = {
  OS: "OS",
  MIDDLEWARE: "ミドルウェア",
  RUNTIME: "ランタイム",
  PACKAGE: "パッケージ",
} as const;

// データ更新日
export const MOCK_LAST_UPDATED = "2025-12-18";

export const MOCK_SERVICES = [
  {
    id: "s1",
    name: "ECサイト フロントエンド",
    dependencies: [
      {
        id: 101,
        name: "Node.js",
        version: "16.x",
        category: CATEGORIES.RUNTIME,
        eol: "2023-09-11",
        isSupported: true,
        note: "v20へ移行中",
      },
      {
        id: 102,
        name: "React",
        version: "18.x",
        category: CATEGORIES.PACKAGE,
        eol: "2026-06-01",
        isSupported: true,
        note: "",
      },
      {
        id: 103,
        name: "Next.js",
        version: "13.x",
        category: CATEGORIES.PACKAGE,
        eol: "2024-12-01",
        isSupported: true,
        note: "LTS",
      },
      {
        id: 104,
        name: "some-internal-lib",
        version: "1.0.0",
        category: CATEGORIES.PACKAGE,
        eol: "",
        isSupported: false,
        note: "社内ライブラリ",
      },
    ],
  },
  {
    id: "s2",
    name: "在庫管理システム API",
    dependencies: [
      {
        id: 201,
        name: "Python",
        version: "3.8",
        category: CATEGORIES.RUNTIME,
        eol: "2024-10-07",
        isSupported: true,
        note: "要アップデート",
      },
      {
        id: 202,
        name: "PostgreSQL",
        version: "11",
        category: CATEGORIES.MIDDLEWARE,
        eol: "2023-11-09",
        isSupported: true,
        note: "EOL到達済み",
      },
      {
        id: 203,
        name: "Django",
        version: "3.2 LTS",
        category: CATEGORIES.PACKAGE,
        eol: "2024-04-01",
        isSupported: true,
        note: "期限間近",
      },
    ],
  },
  {
    id: "s3",
    name: "社内ポータル (Legacy)",
    dependencies: [
      {
        id: 301,
        name: "CentOS",
        version: "7",
        category: CATEGORIES.OS,
        eol: "2024-06-30",
        isSupported: true,
        note: "RHELへ移行予定",
      },
      {
        id: 302,
        name: "PHP",
        version: "7.4",
        category: CATEGORIES.RUNTIME,
        eol: "2022-11-28",
        isSupported: true,
        note: "深刻なリスクあり",
      },
      {
        id: 303,
        name: "Apache",
        version: "2.4",
        category: CATEGORIES.MIDDLEWARE,
        eol: "",
        isSupported: true,
        note: "継続サポート",
      },
      {
        id: 304,
        name: "legacy-framework",
        version: "2.1",
        category: CATEGORIES.PACKAGE,
        eol: "",
        isSupported: false,
        note: "EOL情報不明",
      },
    ],
  },
  {
    id: "s4",
    name: "モバイルアプリ (iOS/Android)",
    dependencies: [
      {
        id: 401,
        name: "React Native",
        version: "0.72",
        category: CATEGORIES.PACKAGE,
        eol: "",
        isSupported: true,
        note: "継続的更新",
      },
      {
        id: 402,
        name: "TypeScript",
        version: "5.x",
        category: CATEGORIES.RUNTIME,
        eol: "",
        isSupported: true,
        note: "",
      },
      {
        id: 403,
        name: "React",
        version: "18.x",
        category: CATEGORIES.PACKAGE,
        eol: "2026-06-01",
        isSupported: true,
        note: "Web版と同じバージョン",
      },
    ],
  },
];

// 期限切れのみのデータ
export const MOCK_SERVICES_EXPIRED_ONLY = [
  {
    id: "s1",
    name: "レガシーシステム",
    dependencies: [
      {
        id: 101,
        name: "PHP",
        version: "5.6",
        category: CATEGORIES.RUNTIME,
        eol: "2018-12-31",
        isSupported: true,
        note: "深刻なセキュリティリスク",
      },
      {
        id: 102,
        name: "MySQL",
        version: "5.5",
        category: CATEGORIES.MIDDLEWARE,
        eol: "2018-12-03",
        isSupported: true,
        note: "即時対応必要",
      },
      {
        id: 103,
        name: "CentOS",
        version: "6",
        category: CATEGORIES.OS,
        eol: "2020-11-30",
        isSupported: true,
        note: "EOL到達済み",
      },
    ],
  },
];

// サポート中のみのデータ
export const MOCK_SERVICES_SAFE_ONLY = [
  {
    id: "s1",
    name: "最新システム",
    dependencies: [
      {
        id: 101,
        name: "Node.js",
        version: "22.x",
        category: CATEGORIES.RUNTIME,
        eol: "2027-04-30",
        isSupported: true,
        note: "最新LTS",
      },
      {
        id: 102,
        name: "React",
        version: "19.x",
        category: CATEGORIES.PACKAGE,
        eol: "2028-06-01",
        isSupported: true,
        note: "",
      },
      {
        id: 103,
        name: "Ubuntu",
        version: "24.04 LTS",
        category: CATEGORIES.OS,
        eol: "2029-04-01",
        isSupported: true,
        note: "最新LTS",
      },
      {
        id: 104,
        name: "PostgreSQL",
        version: "16",
        category: CATEGORIES.MIDDLEWARE,
        eol: "2028-11-09",
        isSupported: true,
        note: "",
      },
    ],
  },
];

// 空のデータ
export const MOCK_SERVICES_EMPTY: typeof MOCK_SERVICES = [];

// 大量データ
const categoryList = [CATEGORIES.OS, CATEGORIES.MIDDLEWARE, CATEGORIES.RUNTIME, CATEGORIES.PACKAGE];

export const MOCK_SERVICES_MANY = Array.from({ length: 10 }, (_, i) => ({
  id: `s${i + 1}`,
  name: `サービス ${i + 1}`,
  dependencies: [
    {
      id: i * 100 + 1,
      name: `Dep-${i + 1}`,
      version: `${i + 1}.0`,
      category: categoryList[i % categoryList.length],
      eol: new Date(Date.now() + (i - 5) * 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
      isSupported: true,
      note: "",
    },
  ],
}));
