import { useEffect, useMemo, useRef, useState } from "react";

const pageOptions = ["top", "team", "vulnerabilities", "eol", "todos"];
const teams = ["Alpha Team", "Growth Team", "Product Team", "Ops Team"];

const severityClass = {
  Critical: "bg-rose-50 text-rose-700 ring-rose-100",
  High: "bg-orange-50 text-orange-700 ring-orange-100",
  Medium: "bg-amber-50 text-amber-700 ring-amber-100",
  Low: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  Unknown: "bg-slate-100 text-slate-600 ring-slate-200",
};

const pageMeta = {
  top: {
    title: "SBOM管理",
    eyebrow: "SBOM Management",
    crumb: "Dashboard / SBOM Management",
  },
  team: {
    title: "チーム管理",
    eyebrow: "Team Management",
    crumb: "Dashboard / Team Management",
  },
  vulnerabilities: {
    title: "脆弱性一覧",
    eyebrow: "Vulnerabilities",
    crumb: "Dashboard / Vulnerabilities",
  },
  eol: {
    title: "EOL一覧",
    eyebrow: "End of Life",
    crumb: "Dashboard / EOL",
  },
  todos: {
    title: "TODO一覧",
    eyebrow: "Remediation TODO",
    crumb: "Dashboard / TODO",
  },
};

const generatedPackageNames = [
  "lodash",
  "date-fns",
  "zod",
  "react-dom",
  "react-router-dom",
  "lucide-react",
  "clsx",
  "zustand",
  "immer",
  "tanstack-query",
  "radix-ui-dialog",
  "radix-ui-dropdown",
  "radix-ui-tabs",
  "eslint",
  "typescript",
  "postcss",
  "autoprefixer",
  "rollup",
  "esbuild",
  "vitest",
  "playwright",
  "storybook",
  "msw",
  "prettier",
  "sharp",
  "framer-motion",
  "d3",
  "chart.js",
  "dayjs",
  "uuid",
  "nanoid",
  "fast-glob",
  "minimatch",
  "yaml",
  "semver",
  "debug",
  "dotenv",
  "pino",
  "winston",
  "helmet",
  "cors",
  "cookie",
  "bcryptjs",
  "argon2",
  "jose",
  "passport",
  "nodemailer",
  "bullmq",
  "ioredis",
  "pg",
  "mysql2",
  "sqlite3",
  "knex",
  "sequelize",
  "mongoose",
  "ajv",
  "openapi-types",
  "swagger-ui",
  "prom-client",
  "opentelemetry-api",
  "sentry-node",
  "aws-sdk",
  "google-auth-library",
  "stripe",
  "twilio",
  "sendgrid",
  "compression",
  "multer",
  "busboy",
  "form-data",
  "qs",
  "validator",
  "sanitize-html",
  "dompurify",
  "marked",
  "remark",
  "rehype",
  "unified",
  "execa",
  "cross-spawn",
  "chokidar",
  "fs-extra",
  "glob",
  "tar",
  "adm-zip",
  "node-fetch",
  "undici",
  "ws",
  "socket.io",
  "graphql",
  "apollo-server",
  "fastify",
  "hono",
  "koa",
  "nestjs-core",
  "rxjs",
  "class-validator",
  "class-transformer",
  "reflect-metadata",
  "cron",
  "luxon",
  "decimal.js",
  "big.js",
  "papaparse",
  "csv-parse",
  "xlsx",
  "pdfkit",
  "puppeteer",
  "cheerio",
  "jsdom",
  "linkedom",
  "tiny-invariant",
  "mitt",
  "valtio",
  "jotai",
  "redux-toolkit",
  "formik",
  "react-hook-form",
  "yup",
  "i18next",
  "next-auth",
  "next-intl",
];

function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

const tailwindCdnScriptId = "sbom-dashboard-tailwind-cdn";
const storyGlobalStyleId = "sbom-dashboard-global-style";

function ensureStoryGlobalStyle() {
  if (document.getElementById(storyGlobalStyleId)) return;

  const style = document.createElement("style");
  style.id = storyGlobalStyleId;
  style.textContent = `
    *, *::before, *::after { box-sizing: border-box; }
    html, body { width: 100%; max-width: 100%; overflow-x: hidden; }
    img, svg, table { max-width: 100%; }
    body { margin: 0; background: #f8fafc; }
    .shadow-soft { box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08); }
    .sbom-storybook-shadow-soft { box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08); }
  `;
  document.head.appendChild(style);
}

function TailwindCdnGate({ children }) {
  const [ready, setReady] = useState(
    () =>
      typeof window !== "undefined" &&
      (Boolean(window.tailwind) ||
        document.getElementById(tailwindCdnScriptId)?.dataset.loaded === "true"),
  );

  useEffect(() => {
    ensureStoryGlobalStyle();

    if (window.tailwind) return undefined;

    const existingScript = document.getElementById(tailwindCdnScriptId);
    const script = existingScript || document.createElement("script");

    const handleLoad = () => {
      script.dataset.loaded = "true";
      setReady(true);
    };

    script.addEventListener("load", handleLoad);

    if (!existingScript) {
      script.id = tailwindCdnScriptId;
      script.src = "https://cdn.tailwindcss.com";
      document.head.appendChild(script);
    }

    return () => {
      script.removeEventListener("load", handleLoad);
    };
  }, []);

  return ready ? children : null;
}

function makeGeneratedDependency(index, prefix) {
  const name = generatedPackageNames[index % generatedPackageNames.length];
  const severities = ["Low", "Low", "Low", "Medium", "Medium", "High", "Unknown"];
  const licenses = ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC", "MPL-2.0"];
  const scopes = ["runtime", "runtime", "build", "dev", "test"];
  const types = ["npm", "npm", "npm", "container", "library"];

  return {
    id: `dep-${prefix}-${String(index + 1).padStart(3, "0")}`,
    name: `${name}${index >= generatedPackageNames.length ? `-${Math.floor(index / generatedPackageNames.length) + 1}` : ""}`,
    version: `${1 + (index % 9)}.${index % 18}.${index % 27}`,
    type: types[index % types.length],
    license: licenses[index % licenses.length],
    severity: index % 53 === 0 ? "Critical" : severities[index % severities.length],
    scope: scopes[index % scopes.length],
    description: `${name} は ${prefix === "web" ? "フロントエンド" : "バックエンド"} SBOMに含まれる依存コンポーネントです。バージョン、ライセンス、利用スコープ、重大度を確認できます。`,
    tags: [
      types[index % types.length],
      scopes[index % scopes.length],
      licenses[index % licenses.length].toLowerCase(),
    ],
    imageLabel: name.slice(0, 3).toUpperCase(),
  };
}

function createInitialSboms() {
  const sboms = [
    {
      id: "sbom-web",
      name: "frontend-app.sbom.json",
      format: "CycloneDX",
      uploadedAt: "2026-06-03 09:40",
      description: "Webフロントエンドの依存関係。React、Vite、Tailwind関連のパッケージを含みます。",
      deployments: [
        {
          name: "production-web",
          region: "ap-northeast-1",
          status: "稼働中",
          image: "ghcr.io/example/frontend:1.8.2",
        },
        {
          name: "staging-web",
          region: "ap-northeast-1",
          status: "検証中",
          image: "ghcr.io/example/frontend:1.9.0-rc",
        },
        {
          name: "preview-env",
          region: "edge",
          status: "一時停止",
          image: "ghcr.io/example/frontend:pr-421",
        },
      ],
      dependencies: [
        {
          id: "dep-react",
          name: "react",
          version: "18.3.1",
          type: "npm",
          license: "MIT",
          severity: "Low",
          scope: "runtime",
          description:
            "UIコンポーネントを構築するためのJavaScriptライブラリ。主要画面の描画基盤として利用されています。",
          tags: ["frontend", "runtime", "ui"],
          imageLabel: "React",
        },
        {
          id: "dep-vite",
          name: "vite",
          version: "5.4.11",
          type: "npm",
          license: "MIT",
          severity: "Medium",
          scope: "build",
          description:
            "フロントエンド向けビルドツール。開発サーバーと本番ビルドの生成に利用されています。",
          tags: ["build", "frontend", "tooling"],
          imageLabel: "Vite",
        },
        {
          id: "dep-tailwind",
          name: "tailwindcss",
          version: "3.4.17",
          type: "npm",
          license: "MIT",
          severity: "Low",
          scope: "build",
          description:
            "ユーティリティファーストCSSフレームワーク。デザインシステムのスタイリングに利用されています。",
          tags: ["css", "design-system", "build"],
          imageLabel: "TW",
        },
        {
          id: "dep-axios",
          name: "axios",
          version: "1.7.9",
          type: "npm",
          license: "MIT",
          severity: "High",
          scope: "runtime",
          description:
            "HTTPクライアントライブラリ。API連携、認証済みリクエスト、エラー処理に利用されています。",
          tags: ["network", "runtime", "api"],
          imageLabel: "AX",
        },
      ],
    },
    {
      id: "sbom-api",
      name: "backend-api.spdx.json",
      format: "SPDX",
      uploadedAt: "2026-06-03 10:12",
      description:
        "バックエンドAPIのSBOM。Node.jsランタイム、認証、ORM、監視関連の依存関係を含みます。",
      deployments: [
        {
          name: "api-production",
          region: "ap-northeast-1",
          status: "稼働中",
          image: "registry.example.com/api:3.12.0",
        },
        {
          name: "api-worker",
          region: "ap-northeast-1",
          status: "稼働中",
          image: "registry.example.com/api-worker:3.12.0",
        },
      ],
      dependencies: [
        {
          id: "dep-express",
          name: "express",
          version: "4.19.2",
          type: "npm",
          license: "MIT",
          severity: "Medium",
          scope: "runtime",
          description:
            "HTTP APIのルーティングとミドルウェア構成を担うWebアプリケーションフレームワーク。",
          tags: ["api", "runtime", "server"],
          imageLabel: "EX",
        },
        {
          id: "dep-prisma",
          name: "prisma",
          version: "5.22.0",
          type: "npm",
          license: "Apache-2.0",
          severity: "Low",
          scope: "runtime",
          description: "DBスキーマ管理と型安全なクエリ生成に利用されるORMツールキット。",
          tags: ["database", "orm", "runtime"],
          imageLabel: "DB",
        },
        {
          id: "dep-jsonwebtoken",
          name: "jsonwebtoken",
          version: "9.0.2",
          type: "npm",
          license: "MIT",
          severity: "Critical",
          scope: "runtime",
          description:
            "JWTの署名・検証に利用される認証関連ライブラリ。認可処理の中核に位置します。",
          tags: ["auth", "security", "jwt"],
          imageLabel: "JWT",
        },
      ],
    },
  ];

  padDependenciesTo(sboms, "sbom-web", 96, "web");
  padDependenciesTo(sboms, "sbom-api", 112, "api");

  return sboms;
}

function padDependenciesTo(sboms, sbomId, targetCount, prefix) {
  const sbom = sboms.find((item) => item.id === sbomId);
  if (!sbom) return;

  const existingNames = new Set(sbom.dependencies.map((dep) => dep.name));
  let index = 0;

  while (sbom.dependencies.length < targetCount) {
    const dep = makeGeneratedDependency(index, prefix);
    if (!existingNames.has(dep.name)) {
      sbom.dependencies.push(dep);
      existingNames.add(dep.name);
    }
    index += 1;
  }
}

function dependencyImage(label) {
  const safeLabel = encodeURIComponent(label || "PKG");
  return `data:image/svg+xml;utf8,
    <svg xmlns='http://www.w3.org/2000/svg' width='520' height='280' viewBox='0 0 520 280'>
      <defs>
        <linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>
          <stop offset='0%' stop-color='%2306b6d4'/>
          <stop offset='55%' stop-color='%236366f1'/>
          <stop offset='100%' stop-color='%230f172a'/>
        </linearGradient>
        <filter id='shadow' x='-20%' y='-20%' width='140%' height='140%'>
          <feDropShadow dx='0' dy='18' stdDeviation='18' flood-color='%230f172a' flood-opacity='0.18'/>
        </filter>
      </defs>
      <rect width='520' height='280' rx='32' fill='%23f8fafc'/>
      <circle cx='438' cy='58' r='88' fill='%23e0f2fe'/>
      <circle cx='72' cy='230' r='110' fill='%23ecfeff'/>
      <g filter='url(%23shadow)'>
        <rect x='124' y='58' width='272' height='164' rx='28' fill='url(%23g)'/>
        <rect x='154' y='88' width='212' height='18' rx='9' fill='white' opacity='.42'/>
        <rect x='154' y='124' width='128' height='18' rx='9' fill='white' opacity='.28'/>
        <rect x='154' y='160' width='176' height='18' rx='9' fill='white' opacity='.28'/>
        <text x='260' y='151' text-anchor='middle' dominant-baseline='middle'
          font-family='Arial, sans-serif' font-size='46' font-weight='700' fill='white'>${safeLabel}</text>
      </g>
    </svg>`.replace(/\s+/g, " ");
}

function normalizeSeverity(value) {
  const raw = String(value || "").toLowerCase();
  if (raw.includes("critical")) return "Critical";
  if (raw.includes("high")) return "High";
  if (raw.includes("medium") || raw.includes("moderate")) return "Medium";
  if (raw.includes("low")) return "Low";
  return "Unknown";
}

function detectLicense(component) {
  if (component.licenses && component.licenses.length) {
    const first = component.licenses[0];
    if (first.license && first.license.id) return first.license.id;
    if (first.license && first.license.name) return first.license.name;
    if (first.expression) return first.expression;
  }
  if (component.licenseConcluded) return component.licenseConcluded;
  if (component.licenseDeclared) return component.licenseDeclared;
  return "Unknown";
}

function guessType(value) {
  const text = String(value || "").toLowerCase();
  if (text.includes("pkg:npm") || text.includes("@") || text.includes("node_modules")) return "npm";
  if (text.includes("pkg:pypi") || text.includes("python")) return "pypi";
  if (text.includes("pkg:maven") || text.includes("java")) return "maven";
  if (text.includes("pkg:golang") || text.includes("go.")) return "go";
  if (text.includes("pkg:docker") || text.includes("container")) return "container";
  return "";
}

function generateDeployments(fileName) {
  const base =
    fileName
      .replace(/\.[^.]+$/, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "") || "sbom";

  return [
    {
      name: `${base}-production`,
      region: "ap-northeast-1",
      status: "未確認",
      image: `registry.example.com/${base}:latest`,
    },
    {
      name: `${base}-staging`,
      region: "ap-northeast-1",
      status: "未確認",
      image: `registry.example.com/${base}:staging`,
    },
  ];
}

function parseCycloneDx(json, fileName) {
  const components = Array.isArray(json.components) ? json.components : [];

  return {
    id: `sbom-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    name: fileName,
    format: json.bomFormat || "CycloneDX",
    uploadedAt: new Date().toLocaleString("ja-JP"),
    description:
      json.metadata && json.metadata.component
        ? `${json.metadata.component.name || fileName} のSBOM。アップロードファイルから依存関係を抽出しました。`
        : "アップロードファイルから依存関係を抽出しました。",
    deployments: generateDeployments(fileName),
    dependencies: components.map((component, index) => ({
      id: `dep-${Date.now()}-${index}`,
      name: component.name || component.purl || `component-${index + 1}`,
      version: component.version || "Unknown",
      type: component.type || guessType(component.purl) || "component",
      license: detectLicense(component),
      severity: normalizeSeverity(component.severity || component.risk || component.rating),
      scope: component.scope || "runtime",
      description:
        component.description ||
        `${component.name || "Component"} は ${fileName} に含まれる依存コンポーネントです。`,
      tags: [component.type || "component", component.scope || "runtime", detectLicense(component)]
        .filter(Boolean)
        .slice(0, 3),
      imageLabel: (component.name || "PKG").slice(0, 3).toUpperCase(),
    })),
  };
}

function parseSpdx(json, fileName) {
  const packages = Array.isArray(json.packages) ? json.packages : [];

  return {
    id: `sbom-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    name: fileName,
    format: "SPDX",
    uploadedAt: new Date().toLocaleString("ja-JP"),
    description: `${fileName} からSPDXパッケージ情報を抽出しました。`,
    deployments: generateDeployments(fileName),
    dependencies: packages.map((pkg, index) => ({
      id: `dep-${Date.now()}-${index}`,
      name: pkg.name || `package-${index + 1}`,
      version: pkg.versionInfo || "Unknown",
      type: "package",
      license: pkg.licenseConcluded || pkg.licenseDeclared || "Unknown",
      severity: "Unknown",
      scope: "runtime",
      description:
        pkg.description || `${pkg.name || "Package"} は ${fileName} に含まれるSPDXパッケージです。`,
      tags: [
        "spdx",
        "package",
        pkg.downloadLocation && pkg.downloadLocation !== "NOASSERTION" ? "source" : "no-source",
      ],
      imageLabel: (pkg.name || "PKG").slice(0, 3).toUpperCase(),
    })),
  };
}

function parseTextSbom(text, fileName) {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const candidates = lines
    .filter(
      (line) =>
        !line.startsWith("#") &&
        !line.startsWith("{") &&
        !line.startsWith("}") &&
        line.length < 160,
    )
    .slice(0, 60);

  return {
    id: `sbom-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    name: fileName,
    format: "Text",
    uploadedAt: new Date().toLocaleString("ja-JP"),
    description: `${fileName} のテキスト内容から依存関係候補を抽出しました。`,
    deployments: generateDeployments(fileName),
    dependencies: candidates.map((line, index) => {
      const match = line.match(/^(@?[\w./-]+)[@:=\s]+([\w.+~^-]+)?/);
      const name = match ? match[1] : line.split(/\s+/)[0];
      const version = match && match[2] ? match[2] : "Unknown";

      return {
        id: `dep-${Date.now()}-${index}`,
        name,
        version,
        type: guessType(name) || "package",
        license: "Unknown",
        severity: "Unknown",
        scope: "runtime",
        description: `${name} はアップロードされたテキストから抽出された依存関係候補です。`,
        tags: ["uploaded", "parsed", "candidate"],
        imageLabel: name.slice(0, 3).toUpperCase(),
      };
    }),
  };
}

function parseUploadedSbom(text, fileName) {
  let parsed;

  try {
    const json = JSON.parse(text);
    if (json.bomFormat || Array.isArray(json.components)) {
      parsed = parseCycloneDx(json, fileName);
    } else if (Array.isArray(json.packages) || json.spdxVersion) {
      parsed = parseSpdx(json, fileName);
    } else {
      parsed = parseTextSbom(text, fileName);
    }
  } catch {
    parsed = parseTextSbom(text, fileName);
  }

  if (!parsed.dependencies.length) {
    parsed.dependencies = [
      {
        id: `dep-${Date.now()}-empty`,
        name: "依存関係なし",
        version: "-",
        type: "unknown",
        license: "Unknown",
        severity: "Unknown",
        scope: "unknown",
        description:
          "アップロードされたSBOMから依存関係を抽出できませんでした。ファイル形式を確認してください。",
        tags: ["empty", "uploaded"],
        imageLabel: "N/A",
      },
    ];
  }

  return parsed;
}

function Icon({ type, className = "h-5 w-5" }) {
  const common = {
    className,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.8",
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": "true",
  };

  if (type === "home") {
    return (
      <svg {...common}>
        <path d="m3 11 9-8 9 8" />
        <path d="M5 10.5V20h5v-5h4v5h5v-9.5" />
      </svg>
    );
  }

  if (type === "team") {
    return (
      <svg {...common}>
        <path d="M8 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z" />
        <path d="M16.5 12a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z" />
        <path d="M2.5 20.5A6.5 6.5 0 0 1 9 14h.4a6.5 6.5 0 0 1 6.1 4.3" />
        <path d="M15.3 14.8a5.5 5.5 0 0 1 6.2 5.45" />
      </svg>
    );
  }

  if (type === "alert") {
    return (
      <svg {...common}>
        <path d="M12 3 21 12 12 21 3 12 12 3Z" />
        <path d="M12 8v5" />
        <path d="M12 16.5h.01" />
      </svg>
    );
  }

  if (type === "calendar") {
    return (
      <svg {...common}>
        <path d="M7 3v3M17 3v3M4 9h16" />
        <rect x="4" y="5" width="16" height="16" rx="2" />
        <path d="m12 12-2.5 4h5L12 12Z" />
      </svg>
    );
  }

  if (type === "todo") {
    return (
      <svg {...common}>
        <rect x="5" y="3" width="14" height="18" rx="2" />
        <path d="m8 9 1.5 1.5L13 7" />
        <path d="m8 16 1.5 1.5L13 14" />
      </svg>
    );
  }

  return (
    <svg {...common}>
      <rect x="4" y="4" width="5.5" height="5.5" rx="1.4" />
      <rect x="14.5" y="4" width="5.5" height="5.5" rx="1.4" />
      <rect x="4" y="14.5" width="5.5" height="5.5" rx="1.4" />
      <rect x="14.5" y="14.5" width="5.5" height="5.5" rx="1.4" />
    </svg>
  );
}

function MenuItem({ active, icon, iconClass, label, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "menu-item flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-left text-sm transition",
        active
          ? "bg-cyan-50 font-semibold text-cyan-800 ring-1 ring-cyan-100 hover:bg-cyan-50"
          : "font-medium text-slate-700 hover:bg-slate-50",
      )}
    >
      <span className={cn("grid h-9 w-9 place-items-center rounded-xl", iconClass)}>
        <Icon type={icon} />
      </span>
      {label}
    </button>
  );
}

function SbomDashboardStory({
  initialTeam = "Alpha Team",
  initialSbomId = "sbom-web",
  initialDependencyId = "dep-react",
}) {
  const fileInputRef = useRef(null);
  const [sboms, setSboms] = useState(() => createInitialSboms());
  const [activePage, setActivePage] = useState("top");
  const [activeTeam, setActiveTeam] = useState(initialTeam);
  const [activeSbomId, setActiveSbomId] = useState(initialSbomId);
  const [activeDependencyId, setActiveDependencyId] = useState(initialDependencyId);
  const [dependencyPage, setDependencyPage] = useState(1);
  const [dependencyPageSize, setDependencyPageSize] = useState(25);
  const [dependencySearchQuery, setDependencySearchQuery] = useState("");
  const [pageMenuOpen, setPageMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const sbom = useMemo(
    () => sboms.find((item) => item.id === activeSbomId) || sboms[0] || null,
    [activeSbomId, sboms],
  );

  const dependency = useMemo(() => {
    if (!sbom || !sbom.dependencies.length) return null;
    return sbom.dependencies.find((dep) => dep.id === activeDependencyId) || sbom.dependencies[0];
  }, [activeDependencyId, sbom]);

  const dependencyPageData = useMemo(() => {
    if (!sbom) {
      return {
        items: [],
        totalItems: 0,
        totalPages: 1,
        currentPage: 1,
        startIndex: 0,
        endIndex: 0,
      };
    }

    const filtered = sbom.dependencies.filter((dep) =>
      dependencyMatches(dep, dependencySearchQuery),
    );
    const totalItems = filtered.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / dependencyPageSize));
    const currentPage = Math.min(Math.max(1, dependencyPage), totalPages);
    const startIndex = (currentPage - 1) * dependencyPageSize;
    const endIndex = Math.min(startIndex + dependencyPageSize, totalItems);

    return {
      items: filtered.slice(startIndex, endIndex),
      totalItems,
      totalPages,
      currentPage,
      startIndex,
      endIndex,
    };
  }, [dependencyPage, dependencyPageSize, dependencySearchQuery, sbom]);

  const meta = pageMeta[activePage] || pageMeta.top;
  const criticalCount = sbom
    ? sbom.dependencies.filter((dep) => dep.severity === "Critical").length
    : 0;

  function routeTo(page) {
    setActivePage(pageOptions.includes(page) ? page : "top");
    setPageMenuOpen(false);
    setUserMenuOpen(false);
  }

  function triggerUpload() {
    fileInputRef.current?.click();
  }

  async function handleUpload(files) {
    const selectedFiles = Array.from(files || []);
    const parsedSboms = [];

    for (const file of selectedFiles) {
      const text = await file.text();
      parsedSboms.push(parseUploadedSbom(text, file.name));
    }

    if (!parsedSboms.length) return;

    const last = parsedSboms[parsedSboms.length - 1];
    setSboms((current) => [...current, ...parsedSboms]);
    setActiveSbomId(last.id);
    setActiveDependencyId(last.dependencies[0]?.id || "");
    setDependencyPage(1);
    setDependencySearchQuery("");
    routeTo("top");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function selectSbom(sbomId) {
    const selected = sboms.find((item) => item.id === sbomId);
    setActiveSbomId(sbomId);
    setActiveDependencyId(selected?.dependencies[0]?.id || "");
    setDependencyPage(1);
    setDependencySearchQuery("");
  }

  function selectFirstVisibleDependency(nextPageData = dependencyPageData) {
    if (
      nextPageData.items.length &&
      !nextPageData.items.some((dep) => dep.id === activeDependencyId)
    ) {
      setActiveDependencyId(nextPageData.items[0].id);
    }
  }

  function updateSearch(value) {
    setDependencySearchQuery(value);
    setDependencyPage(1);

    if (!sbom) return;
    const filtered = sbom.dependencies.filter((dep) => dependencyMatches(dep, value));
    if (filtered.length && !filtered.some((dep) => dep.id === activeDependencyId)) {
      setActiveDependencyId(filtered[0].id);
    }
  }

  function updatePageSize(value) {
    const nextSize = Number(value) || 25;
    setDependencyPageSize(nextSize);
    setDependencyPage(1);
    selectFirstVisibleDependency();
  }

  function setPageNumber(pageNumber) {
    setDependencyPage(Math.min(Math.max(1, pageNumber), dependencyPageData.totalPages));
    selectFirstVisibleDependency();
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-slate-50 font-sans text-slate-900 antialiased">
      <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-4 py-3 md:px-8 md:py-4">
          <div className="flex items-center justify-between gap-2 md:gap-3">
            <div className="relative shrink-0">
              <button
                type="button"
                className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white text-cyan-600 shadow-sm transition hover:border-cyan-200 hover:bg-cyan-50"
                aria-label="アプリメニュー"
                aria-expanded={pageMenuOpen}
                onClick={(event) => {
                  event.stopPropagation();
                  setUserMenuOpen(false);
                  setPageMenuOpen((open) => !open);
                }}
              >
                <Icon type="grid" />
              </button>

              <div
                className={cn(
                  "absolute left-0 mt-2 w-[min(18rem,calc(100vw-2rem))] overflow-hidden rounded-3xl border border-slate-200 bg-white p-2 text-slate-900 shadow-soft sbom-storybook-shadow-soft",
                  !pageMenuOpen && "hidden",
                )}
              >
                <MenuItem
                  active={activePage === "top"}
                  icon="home"
                  iconClass="bg-cyan-500 text-white"
                  label="SBOM管理"
                  onClick={() => routeTo("top")}
                />
                <MenuItem
                  active={activePage === "team"}
                  icon="team"
                  iconClass="bg-slate-100 text-slate-600"
                  label="チーム管理"
                  onClick={() => routeTo("team")}
                />
                <MenuItem
                  active={activePage === "vulnerabilities"}
                  icon="alert"
                  iconClass="bg-rose-50 text-rose-600"
                  label="脆弱性一覧"
                  onClick={() => routeTo("vulnerabilities")}
                />
                <MenuItem
                  active={activePage === "eol"}
                  icon="calendar"
                  iconClass="bg-amber-50 text-amber-600"
                  label="EOL一覧"
                  onClick={() => routeTo("eol")}
                />
                <MenuItem
                  active={activePage === "todos"}
                  icon="todo"
                  iconClass="bg-cyan-50 text-cyan-600"
                  label="TODO一覧"
                  onClick={() => routeTo("todos")}
                />

                <div className="my-2 h-px bg-slate-100" />

                <p className="px-3 py-2 text-xs font-medium text-slate-400">チームへのおすすめ</p>
                <div className="rounded-2xl bg-cyan-50 p-3 ring-1 ring-cyan-100">
                  <p className="text-sm font-medium text-slate-900">Critical Remediation</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Critical / High の脆弱性から対応TODOを作成します。
                  </p>
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => routeTo("top")}
              className="flex min-w-0 flex-1 items-center gap-3 text-left"
            >
              <div className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-cyan-500 font-bold text-white shadow-sm">
                S
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold tracking-wide text-slate-950">
                  SBOM Console
                </p>
                <p className="hidden truncate text-xs text-slate-500 md:block">{meta.crumb}</p>
              </div>
            </button>

            <div className="flex shrink-0 items-center gap-2 md:gap-3">
              <label
                className="hidden text-xs font-medium uppercase tracking-wider text-slate-400 md:inline"
                htmlFor="team-select"
              >
                Team
              </label>
              <select
                id="team-select"
                value={activeTeam}
                onChange={(event) => setActiveTeam(event.target.value)}
                className="hidden rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none ring-cyan-500/20 focus:ring-4 md:block"
              >
                {teams.map((team) => (
                  <option key={team}>{team}</option>
                ))}
              </select>

              <div className="relative">
                <button
                  type="button"
                  className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-900 transition hover:bg-slate-50 md:hidden"
                  aria-label="ユーザーメニュー"
                  aria-expanded={userMenuOpen}
                  onClick={(event) => {
                    event.stopPropagation();
                    setPageMenuOpen(false);
                    setUserMenuOpen((open) => !open);
                  }}
                >
                  MT
                </button>

                <div
                  className={cn(
                    "absolute right-0 mt-2 w-56 overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 shadow-soft sbom-storybook-shadow-soft",
                    !userMenuOpen && "hidden",
                  )}
                >
                  <div className="px-3 py-3">
                    <p className="text-sm font-semibold text-slate-950">Mika Tanaka</p>
                    <p className="text-xs text-slate-500">Logged in</p>
                  </div>
                  <div className="h-px bg-slate-100" />
                  <button
                    type="button"
                    className="block w-full rounded-xl px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
                  >
                    プロフィール
                  </button>
                  <button
                    type="button"
                    className="block w-full rounded-xl px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
                  >
                    アカウント設定
                  </button>
                  <button
                    type="button"
                    className="block w-full rounded-xl px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50"
                  >
                    ログアウト
                  </button>
                </div>
              </div>

              <div className="hidden items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 md:flex">
                <div className="grid h-9 w-9 place-items-center rounded-full bg-slate-900 text-xs font-semibold text-white">
                  MT
                </div>
                <div className="text-sm">
                  <p className="font-medium text-slate-950">Mika Tanaka</p>
                  <p className="text-xs text-slate-500">Logged in</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-3 md:hidden">
            <label
              className="mb-1 block text-[11px] font-medium uppercase tracking-wider text-slate-400"
              htmlFor="team-select-mobile"
            >
              Team
            </label>
            <select
              id="team-select-mobile"
              value={activeTeam}
              onChange={(event) => setActiveTeam(event.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-800 outline-none ring-cyan-500/20 focus:ring-4"
            >
              {teams.map((team) => (
                <option key={team}>{team}</option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl overflow-x-hidden px-4 py-6 md:px-8 md:py-8">
        <section className="mb-6 flex flex-col justify-between gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft sbom-storybook-shadow-soft sm:p-5 md:flex-row md:items-center">
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-wider text-cyan-600">
              {meta.eyebrow}
            </p>
            <h1 className="mt-1 truncate text-2xl font-bold text-slate-950 md:text-3xl">
              {meta.title}
            </h1>
          </div>

          <div className="grid w-full min-w-0 grid-cols-3 gap-2 text-center md:w-auto md:gap-3">
            <Metric label="SBOM" value={sboms.length} />
            <Metric label="Dependencies" value={sbom ? sbom.dependencies.length : 0} />
            <Metric label="Critical" value={criticalCount} tone="critical" />
          </div>
        </section>

        <section className="mb-6 rounded-3xl border border-slate-200 bg-white p-5 shadow-soft sbom-storybook-shadow-soft">
          <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
            <div className="min-w-0">
              <p className="text-sm text-slate-500">Current team</p>
              <p className="mt-1 text-lg font-semibold text-slate-950">{activeTeam}</p>
            </div>
            <div className="grid min-w-0 grid-cols-2 gap-2 md:flex md:flex-wrap md:justify-end">
              <button
                type="button"
                onClick={triggerUpload}
                className="min-w-0 rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-600 transition hover:bg-slate-50 md:px-4"
              >
                SBOMアップロード
              </button>
              <button
                type="button"
                className="min-w-0 rounded-xl bg-cyan-500 px-3 py-2 text-sm font-semibold text-white transition hover:bg-cyan-600 md:px-4"
              >
                レポート生成
              </button>
            </div>
          </div>
        </section>

        {activePage === "top" && (
          <SbomPage
            sboms={sboms}
            sbom={sbom}
            dependency={dependency}
            dependencyPageData={dependencyPageData}
            dependencyPageSize={dependencyPageSize}
            dependencySearchQuery={dependencySearchQuery}
            activeSbomId={activeSbomId}
            activeDependencyId={activeDependencyId}
            onSelectSbom={selectSbom}
            onTriggerUpload={triggerUpload}
            onSelectDependency={setActiveDependencyId}
            onSearch={updateSearch}
            onPageSize={updatePageSize}
            onPage={setPageNumber}
            onPrev={() => setPageNumber(dependencyPageData.currentPage - 1)}
            onNext={() => setPageNumber(dependencyPageData.currentPage + 1)}
          />
        )}
        {activePage === "team" && <TeamPage onBack={() => routeTo("top")} />}
        {activePage === "vulnerabilities" && <VulnerabilitiesPage onBack={() => routeTo("top")} />}
        {activePage === "eol" && <EolPage onBack={() => routeTo("top")} />}
        {activePage === "todos" && <TodosPage onBack={() => routeTo("top")} />}
      </main>

      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        multiple
        accept=".json,.xml,.spdx,.txt,application/json,text/xml,application/xml"
        onChange={(event) => handleUpload(event.target.files)}
      />
    </div>
  );
}

function Metric({ label, value, tone }) {
  return (
    <div className="rounded-2xl bg-slate-50 px-2 py-3 md:px-5">
      <p className="text-xs text-slate-500">{label}</p>
      <p
        className={cn(
          "mt-1 text-lg font-bold md:text-xl",
          tone === "critical" ? "text-rose-600" : "text-slate-950",
        )}
      >
        {value}
      </p>
    </div>
  );
}

function SbomPage(props) {
  const {
    sboms,
    sbom,
    dependency,
    dependencyPageData,
    dependencyPageSize,
    dependencySearchQuery,
    activeSbomId,
    activeDependencyId,
    onSelectSbom,
    onTriggerUpload,
    onSelectDependency,
    onSearch,
    onPageSize,
    onPage,
    onPrev,
    onNext,
  } = props;

  if (!sbom) {
    return (
      <section className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center shadow-soft sbom-storybook-shadow-soft">
        <h2 className="text-xl font-semibold text-slate-950">SBOMファイルをアップロード</h2>
        <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-500">
          CycloneDX JSON、SPDX
          JSON、または依存関係リストをアップロードすると、依存関係一覧と詳細情報を表示します。
        </p>
        <button
          type="button"
          onClick={onTriggerUpload}
          className="mt-6 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-white hover:bg-cyan-600"
        >
          ファイルを選択
        </button>
      </section>
    );
  }

  return (
    <>
      <div className="mb-5 max-w-full overflow-hidden">
        <div className="flex max-w-full flex-wrap items-center gap-2 border-b border-slate-200 pb-3 md:flex-nowrap md:pb-2">
          {sboms.map((item) => {
            const active = item.id === activeSbomId;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectSbom(item.id)}
                className={cn(
                  "group flex max-w-full min-w-0 items-center gap-2 rounded-2xl px-3 py-2 text-sm transition md:px-4",
                  active
                    ? "bg-slate-950 text-white shadow-sm"
                    : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50",
                )}
              >
                <span className="max-w-[132px] truncate sm:max-w-[190px]">{item.name}</span>
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-[11px]",
                    active ? "bg-white/15 text-white/80" : "bg-slate-100 text-slate-500",
                  )}
                >
                  {item.dependencies.length}
                </span>
              </button>
            );
          })}

          <button
            type="button"
            onClick={onTriggerUpload}
            className="flex max-w-full min-w-0 items-center gap-2 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-500 transition hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 md:px-4"
          >
            <span className="grid h-5 w-5 place-items-center rounded-full bg-white text-base leading-none shadow-sm">
              +
            </span>
            新規アップロード
          </button>
        </div>
      </div>

      <div className="grid min-w-0 max-w-full gap-5 xl:grid-cols-[minmax(340px,0.9fr)_minmax(0,1.45fr)]">
        <div className="min-w-0 xl:order-2">
          <DependencyTable
            sbom={sbom}
            page={dependencyPageData}
            pageSize={dependencyPageSize}
            searchQuery={dependencySearchQuery}
            activeDependencyId={activeDependencyId}
            onSelectDependency={onSelectDependency}
            onSearch={onSearch}
            onPageSize={onPageSize}
            onPage={onPage}
            onPrev={onPrev}
            onNext={onNext}
          />
        </div>

        <aside className="min-w-0 space-y-5 xl:order-1">
          <DetailCard dep={dependency} />
          <DeploymentsCard sbom={sbom} />
        </aside>
      </div>
    </>
  );
}

function dependencyMatches(dep, query) {
  const q = String(query || "")
    .trim()
    .toLowerCase();
  if (!q) return true;

  return [
    dep.name,
    dep.version,
    dep.type,
    dep.license,
    dep.severity,
    dep.scope,
    dep.description,
    ...(dep.tags || []),
  ]
    .join(" ")
    .toLowerCase()
    .includes(q);
}

function DependencyTable({
  sbom,
  page,
  pageSize,
  searchQuery,
  activeDependencyId,
  onSelectDependency,
  onSearch,
  onPageSize,
  onPage,
  onPrev,
  onNext,
}) {
  return (
    <section className="min-w-0 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft sbom-storybook-shadow-soft sm:p-5">
      <div className="mb-4 flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
        <div className="min-w-0">
          <h2 className="text-lg font-semibold text-slate-950">依存関係一覧</h2>
          <p className="mt-1 truncate text-sm text-slate-500">
            {sbom.name} / {sbom.format} / {sbom.uploadedAt}
          </p>
        </div>

        <div className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_auto] lg:w-[420px]">
          <input
            type="search"
            placeholder="依存関係を検索"
            value={searchQuery}
            onChange={(event) => onSearch(event.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm outline-none ring-cyan-500/20 focus:bg-white focus:ring-4"
          />

          <label className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
            <span className="shrink-0 text-xs text-slate-500">表示</span>
            <select
              value={pageSize}
              onChange={(event) => onPageSize(event.target.value)}
              className="bg-transparent text-sm font-medium text-slate-800 outline-none"
            >
              {[10, 25, 50, 100].map((size) => (
                <option key={size} value={size}>
                  {size}件
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="hidden overflow-x-auto rounded-2xl border border-slate-200 md:block">
        <table className="w-full table-fixed text-left text-sm">
          <colgroup>
            <col className="w-[24%]" />
            <col className="w-[13%]" />
            <col className="w-[12%]" />
            <col className="w-[13%]" />
            <col className="w-[18%]" />
            <col className="w-[20%]" />
          </colgroup>
          <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-3 py-3">Package</th>
              <th className="px-3 py-3">Version</th>
              <th className="px-3 py-3">Type</th>
              <th className="px-3 py-3">License</th>
              <th className="px-3 py-3">Severity</th>
              <th className="px-3 py-3">Scope</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {page.items.length ? (
              page.items.map((dep) => (
                <DependencyRow
                  key={dep.id}
                  dep={dep}
                  active={dep.id === activeDependencyId}
                  onSelect={() => onSelectDependency(dep.id)}
                />
              ))
            ) : (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-sm text-slate-500">
                  該当する依存関係がありません
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="space-y-3 md:hidden">
        {page.items.length ? (
          page.items.map((dep) => (
            <DependencyMobileCard
              key={dep.id}
              dep={dep}
              active={dep.id === activeDependencyId}
              onSelect={() => onSelectDependency(dep.id)}
            />
          ))
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
            該当する依存関係がありません
          </div>
        )}
      </div>

      <DependencyPagination page={page} onPage={onPage} onPrev={onPrev} onNext={onNext} />
    </section>
  );
}

function DependencyRow({ dep, active, onSelect }) {
  const badge = severityClass[dep.severity] || severityClass.Unknown;

  return (
    <tr
      onClick={onSelect}
      className={cn(
        "cursor-pointer transition",
        active ? "bg-cyan-50/80" : "bg-white hover:bg-slate-50",
      )}
    >
      <td className="px-3 py-3">
        <div className="truncate font-semibold text-slate-950">{dep.name}</div>
        <div className="truncate text-xs text-slate-400">{dep.id}</div>
      </td>
      <td className="truncate px-3 py-3 text-slate-600">{dep.version}</td>
      <td className="truncate px-3 py-3 text-slate-600">{dep.type}</td>
      <td className="truncate px-3 py-3 text-slate-600">{dep.license}</td>
      <td className="px-3 py-3">
        <span
          className={cn(
            "inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ring-1",
            badge,
          )}
        >
          {dep.severity}
        </span>
      </td>
      <td className="truncate px-3 py-3 text-slate-600">{dep.scope}</td>
    </tr>
  );
}

function DependencyMobileCard({ dep, active, onSelect }) {
  const badge = severityClass[dep.severity] || severityClass.Unknown;

  return (
    <button
      type="button"
      onClick={onSelect}
      className={cn(
        "block w-full rounded-2xl border p-4 text-left transition",
        active ? "border-cyan-300 bg-cyan-50/80" : "border-slate-200 bg-white hover:bg-slate-50",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate font-semibold text-slate-950">{dep.name}</p>
          <p className="mt-1 truncate text-xs text-slate-400">{dep.id}</p>
        </div>
        <span
          className={cn(
            "shrink-0 whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ring-1",
            badge,
          )}
        >
          {dep.severity}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <SmallFact label="Version" value={dep.version} />
        <SmallFact label="Type" value={dep.type} />
        <SmallFact label="License" value={dep.license} />
        <SmallFact label="Scope" value={dep.scope} />
      </div>
    </button>
  );
}

function SmallFact({ label, value }) {
  return (
    <div className="rounded-xl bg-slate-50 p-3">
      <p className="text-[11px] font-medium uppercase tracking-wider text-slate-400">{label}</p>
      <p className="mt-1 truncate text-slate-700">{value}</p>
    </div>
  );
}

function DependencyPagination({ page, onPage, onPrev, onNext }) {
  const from = page.totalItems === 0 ? 0 : page.startIndex + 1;
  const to = page.endIndex;
  const pageButtons = [];
  const start = Math.max(1, page.currentPage - 1);
  const end = Math.min(page.totalPages, page.currentPage + 1);

  if (start > 1) {
    pageButtons.push(1);
    if (start > 2) pageButtons.push("start-ellipsis");
  }

  for (let pageNumber = start; pageNumber <= end; pageNumber += 1) {
    pageButtons.push(pageNumber);
  }

  if (end < page.totalPages) {
    if (end < page.totalPages - 1) pageButtons.push("end-ellipsis");
    pageButtons.push(page.totalPages);
  }

  return (
    <div className="mt-4 flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm text-slate-500">
        <span className="font-medium text-slate-800">
          {from}-{to}
        </span>{" "}
        / {page.totalItems} 件
      </p>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={onPrev}
          disabled={page.currentPage <= 1}
          className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          前へ
        </button>

        <div className="flex items-center gap-1">
          {pageButtons.map((pageNumber) =>
            typeof pageNumber === "number" ? (
              <button
                key={pageNumber}
                type="button"
                onClick={() => onPage(pageNumber)}
                className={cn(
                  "grid h-9 min-w-9 place-items-center rounded-xl px-3 text-sm transition",
                  pageNumber === page.currentPage
                    ? "bg-slate-950 text-white"
                    : "border border-slate-200 text-slate-600 hover:bg-slate-50",
                )}
              >
                {pageNumber}
              </button>
            ) : (
              <span key={pageNumber} className="px-2 text-sm text-slate-400">
                ...
              </span>
            ),
          )}
        </div>

        <button
          type="button"
          onClick={onNext}
          disabled={page.currentPage >= page.totalPages}
          className="rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          次へ
        </button>
      </div>
    </div>
  );
}

function DetailCard({ dep }) {
  if (!dep) {
    return (
      <section className="min-w-0 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft sbom-storybook-shadow-soft sm:p-5">
        <h2 className="text-lg font-semibold text-slate-950">詳細情報</h2>
        <p className="mt-2 text-sm text-slate-500">依存関係を選択してください。</p>
      </section>
    );
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-soft sbom-storybook-shadow-soft">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-cyan-600">
            Dependency detail
          </p>
          <h2 className="mt-1 text-xl font-bold text-slate-950">{dep.name}</h2>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          {dep.version}
        </span>
      </div>

      <img
        src={dependencyImage(dep.imageLabel)}
        alt={`${dep.name} image`}
        className="mt-5 aspect-[16/9] w-full rounded-2xl border border-slate-200 object-cover"
      />

      <p className="mt-5 text-sm leading-6 text-slate-600">{dep.description}</p>

      <div className="mt-5 flex flex-wrap gap-2">
        {dep.tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-medium text-cyan-700"
          >
            {tag}
          </span>
        ))}
      </div>
    </section>
  );
}

function DeploymentsCard({ sbom }) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-soft sbom-storybook-shadow-soft">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-cyan-600">Deployments</p>
          <h2 className="mt-1 text-lg font-semibold text-slate-950">デプロイ先一覧</h2>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-500">
          {sbom.deployments.length} targets
        </span>
      </div>

      <div className="mt-5 space-y-3">
        {sbom.deployments.map((item) => (
          <div key={item.name} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-semibold text-slate-950">{item.name}</p>
                <p className="mt-1 text-xs text-slate-500">{item.region}</p>
              </div>
              <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200">
                {item.status}
              </span>
            </div>
            <p className="mt-3 max-w-full truncate rounded-xl bg-white px-3 py-2 font-mono text-xs text-slate-500 ring-1 ring-slate-200">
              {item.image}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

function BackButton({ onClick }) {
  return (
    <div className="mb-4 flex items-center justify-between">
      <button
        type="button"
        onClick={onClick}
        className="rounded-xl px-3 py-2 text-sm text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
      >
        ← SBOM管理へ戻る
      </button>
    </div>
  );
}

function TeamPage({ onBack }) {
  const members = [
    ["Mika Tanaka", "Owner", "All SBOMs", "Active"],
    ["Sato Ren", "Security Lead", "Vulnerability", "Active"],
    ["Kimura Aoi", "Developer", "Frontend SBOM", "Active"],
    ["Ito Haru", "Auditor", "Read only", "Pending"],
  ];
  const groups = [
    ["Owner", "全操作、チーム設定、削除権限"],
    ["Security Lead", "脆弱性評価、TODO作成、承認"],
    ["Developer", "SBOM閲覧、修正状況更新"],
    ["Auditor", "閲覧、エクスポートのみ"],
  ];

  return (
    <>
      <BackButton onClick={onBack} />
      <div className="grid gap-6 lg:grid-cols-3">
        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sbom-storybook-shadow-soft lg:col-span-2">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <h2 className="text-lg font-semibold text-slate-950">メンバー一覧</h2>
              <p className="mt-2 text-sm text-slate-500">
                SBOM、脆弱性、EOL対応に関わるチームメンバーと権限を管理します。
              </p>
            </div>
            <button
              type="button"
              className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-600"
            >
              メンバー招待
            </button>
          </div>

          <div className="mt-6 overflow-x-auto rounded-2xl border border-slate-200">
            <table className="w-full min-w-[680px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-5 py-4">Name</th>
                  <th className="px-5 py-4">Role</th>
                  <th className="px-5 py-4">Scope</th>
                  <th className="px-5 py-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {members.map(([name, role, scope, status]) => (
                  <tr key={name}>
                    <td className="px-5 py-4 font-medium text-slate-950">{name}</td>
                    <td className="px-5 py-4 text-slate-600">{role}</td>
                    <td className="px-5 py-4 text-slate-600">{scope}</td>
                    <td className="px-5 py-4">
                      <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-medium text-cyan-700">
                        {status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sbom-storybook-shadow-soft">
          <h2 className="text-lg font-semibold text-slate-950">権限グループ</h2>
          <div className="mt-5 space-y-3">
            {groups.map(([title, desc]) => (
              <div key={title} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="font-semibold text-slate-950">{title}</p>
                <p className="mt-1 text-sm leading-5 text-slate-500">{desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}

function VulnerabilitiesPage({ onBack }) {
  const summary = [
    ["Critical", "3", "text-rose-600 bg-rose-50"],
    ["High", "12", "text-orange-600 bg-orange-50"],
    ["Medium", "31", "text-amber-600 bg-amber-50"],
    ["Resolved", "18", "text-emerald-600 bg-emerald-50"],
  ];
  const vulnerabilities = [
    ["CVE-2026-1042", "jsonwebtoken", "Critical", "9.8", "Open", "9.0.3"],
    ["CVE-2026-0881", "axios", "High", "8.1", "In progress", "1.8.2"],
    ["CVE-2025-7710", "vite", "Medium", "6.4", "Accepted", "5.4.14"],
    ["CVE-2025-6992", "express", "Medium", "5.9", "Open", "4.21.1"],
    ["CVE-2025-4201", "ws", "High", "7.5", "Open", "8.18.1"],
  ];

  return (
    <>
      <BackButton onClick={onBack} />
      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sbom-storybook-shadow-soft">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h2 className="text-lg font-semibold text-slate-950">検出済み脆弱性</h2>
            <p className="mt-2 text-sm text-slate-500">
              SBOM内の依存関係に紐づくCVE、重大度、対応状況を確認します。
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="rounded-xl border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
            >
              重大度で絞り込み
            </button>
            <button
              type="button"
              className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-600"
            >
              TODO化
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-3 md:grid-cols-4">
          {summary.map(([label, value, cls]) => (
            <div key={label} className={cn("rounded-2xl p-4", cls)}>
              <p className="text-xs font-medium uppercase tracking-wider">{label}</p>
              <p className="mt-2 text-2xl font-bold">{value}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 overflow-x-auto rounded-2xl border border-slate-200">
          <table className="w-full min-w-[820px] text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-5 py-4">CVE</th>
                <th className="px-5 py-4">Package</th>
                <th className="px-5 py-4">Severity</th>
                <th className="px-5 py-4">CVSS</th>
                <th className="px-5 py-4">Status</th>
                <th className="px-5 py-4">Fix</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {vulnerabilities.map(([cve, pkg, severity, cvss, status, fix]) => {
                const cls =
                  severity === "Critical"
                    ? "bg-rose-50 text-rose-700"
                    : severity === "High"
                      ? "bg-orange-50 text-orange-700"
                      : "bg-amber-50 text-amber-700";
                return (
                  <tr key={cve}>
                    <td className="px-5 py-4 font-medium text-slate-950">{cve}</td>
                    <td className="px-5 py-4 text-slate-600">{pkg}</td>
                    <td className="px-5 py-4">
                      <span className={cn("rounded-full px-3 py-1 text-xs font-medium", cls)}>
                        {severity}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-slate-600">{cvss}</td>
                    <td className="px-5 py-4 text-slate-600">{status}</td>
                    <td className="px-5 py-4 font-mono text-xs text-slate-500">{fix}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function EolPage({ onBack }) {
  const items = [
    ["Node.js 18", "Runtime", "2025-04-30", "Expired", "bg-rose-50 text-rose-700"],
    ["PostgreSQL 13", "Database", "2025-11-13", "Soon", "bg-amber-50 text-amber-700"],
    ["Vite 5", "Build tool", "2026-02-28", "Watch", "bg-cyan-50 text-cyan-700"],
    ["Express 4", "Framework", "2026-12-31", "Planned", "bg-emerald-50 text-emerald-700"],
  ];

  return (
    <>
      <BackButton onClick={onBack} />
      <div className="grid gap-6 lg:grid-cols-3">
        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sbom-storybook-shadow-soft lg:col-span-2">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <h2 className="text-lg font-semibold text-slate-950">EOL対象コンポーネント</h2>
              <p className="mt-2 text-sm text-slate-500">
                ランタイム、フレームワーク、主要ライブラリのサポート期限を管理します。
              </p>
            </div>
            <button
              type="button"
              className="rounded-xl border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
            >
              CSV出力
            </button>
          </div>

          <div className="mt-6 space-y-3">
            {items.map(([name, type, date, status, cls]) => (
              <div
                key={name}
                className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <p className="font-semibold text-slate-950">{name}</p>
                  <p className="mt-1 text-sm text-slate-500">
                    {type} / EOL: {date}
                  </p>
                </div>
                <span className={cn("w-fit rounded-full px-3 py-1 text-xs font-medium", cls)}>
                  {status}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sbom-storybook-shadow-soft">
          <h2 className="text-lg font-semibold text-slate-950">対応優先度</h2>
          <div className="mt-5 space-y-4">
            <PriorityCard label="期限切れ" value="1" className="bg-rose-50 text-rose-700" />
            <PriorityCard label="90日以内" value="2" className="bg-amber-50 text-amber-700" />
            <PriorityCard label="監視対象" value="8" className="bg-slate-50 text-slate-700" />
          </div>
        </section>
      </div>
    </>
  );
}

function PriorityCard({ label, value, className }) {
  return (
    <div className={cn("rounded-2xl p-4", className)}>
      <p className="text-sm font-semibold">{label}</p>
      <p className="mt-1 text-3xl font-bold">{value}</p>
    </div>
  );
}

function TodosPage({ onBack }) {
  const todos = [
    ["jsonwebtoken を 9.0.3 へ更新", "Critical CVE対応", "Sato Ren", "Today", "High", false],
    ["Node.js 20 移行計画を作成", "EOL対応", "Kimura Aoi", "This week", "High", false],
    ["axios 更新後の回帰テスト", "High CVE対応", "Ito Haru", "Tomorrow", "Medium", false],
    ["SPDXレポートを監査用に出力", "監査対応", "Mika Tanaka", "Friday", "Low", true],
  ];
  const statuses = [
    ["未着手", "9", "bg-slate-50 text-slate-700"],
    ["対応中", "6", "bg-cyan-50 text-cyan-700"],
    ["レビュー待ち", "3", "bg-amber-50 text-amber-700"],
    ["完了", "14", "bg-emerald-50 text-emerald-700"],
  ];

  return (
    <>
      <BackButton onClick={onBack} />
      <div className="grid gap-6 lg:grid-cols-3">
        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sbom-storybook-shadow-soft lg:col-span-2">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <h2 className="text-lg font-semibold text-slate-950">対応TODO</h2>
              <p className="mt-2 text-sm text-slate-500">
                脆弱性、EOL、ライセンス確認から発生した対応タスクを管理します。
              </p>
            </div>
            <button
              type="button"
              className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-600"
            >
              TODO追加
            </button>
          </div>

          <div className="mt-6 space-y-3">
            {todos.map(([title, desc, owner, due, priority, checked]) => {
              const cls =
                priority === "High"
                  ? "bg-rose-50 text-rose-700"
                  : priority === "Medium"
                    ? "bg-amber-50 text-amber-700"
                    : "bg-slate-100 text-slate-600";
              return (
                <label
                  key={title}
                  className="flex cursor-pointer flex-col gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 md:flex-row md:items-center md:justify-between"
                >
                  <div className="flex min-w-0 gap-3">
                    <input
                      type="checkbox"
                      defaultChecked={checked}
                      className="mt-1 h-5 w-5 shrink-0 rounded border-slate-300 text-cyan-500"
                    />
                    <div className="min-w-0">
                      <p className="font-semibold text-slate-950">{title}</p>
                      <p className="mt-1 text-sm text-slate-500">
                        {desc} / {owner} / {due}
                      </p>
                    </div>
                  </div>
                  <span
                    className={cn("w-fit shrink-0 rounded-full px-3 py-1 text-xs font-medium", cls)}
                  >
                    {priority}
                  </span>
                </label>
              );
            })}
          </div>
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sbom-storybook-shadow-soft">
          <h2 className="text-lg font-semibold text-slate-950">ステータス</h2>
          <div className="mt-5 space-y-3">
            {statuses.map(([label, value, cls]) => (
              <div
                key={label}
                className={cn("flex items-center justify-between rounded-2xl p-4", cls)}
              >
                <span className="text-sm font-medium">{label}</span>
                <span className="text-2xl font-bold">{value}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </>
  );
}

const meta = {
  title: "SBOM/SBOM Management Dashboard",
  component: SbomDashboardStory,
  parameters: {
    layout: "fullscreen",
  },
  argTypes: {
    initialTeam: {
      control: "select",
      options: teams,
    },
    initialSbomId: {
      control: "select",
      options: ["sbom-web", "sbom-api"],
    },
    initialDependencyId: {
      control: "text",
    },
  },
  args: {
    initialTeam: "Alpha Team",
    initialSbomId: "sbom-web",
    initialDependencyId: "dep-react",
  },
};

export default meta;

export const Dashboard = {
  render: (args) => (
    <TailwindCdnGate>
      <SbomDashboardStory {...args} />
    </TailwindCdnGate>
  ),
};
