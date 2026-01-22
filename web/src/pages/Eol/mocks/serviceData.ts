// Mock Data for ServiceEolDashboard

export const MOCK_SERVICES_EXPIRED_ONLY = {
  total: 3,
  products: [
    {
      eol_product_id: "8ca0b1eb-3982-5f42-a6a9-02040360e02b",
      name: "PHP",
      product_category: "runtime",
      description:
        "PHP is a popular general-purpose scripting language that is especially suited to web development.",
      is_ecosystem: false,
      matching_name: "PHP",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_php_1",
          version: "5.6",
          release_date: "2014-08-28",
          eol_from: "2018-12-31",
          matching_version: "5.6",
          created_at: "2025-12-03T10:23:45Z",
          updated_at: "2025-12-03T10:23:45Z",
          services: [
            {
              service_id: "service_id_1",
              service_name: "レガシーシステム",
            },
          ],
        },
      ],
    },
    {
      eol_product_id: "9db1c2fc-4093-6g53-b7b0-13151471f13c",
      name: "MySQL",
      product_category: "middleware",
      description: "MySQL is an open-source relational database management system.",
      is_ecosystem: false,
      matching_name: "MySQL",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_mysql_1",
          version: "5.5",
          release_date: "2010-12-15",
          eol_from: "2018-12-03",
          matching_version: "5.5",
          created_at: "2025-12-03T10:23:45Z",
          updated_at: "2025-12-03T10:23:45Z",
          services: [
            {
              service_id: "service_id_2",
              service_name: "顧客管理システム",
            },
          ],
        },
      ],
    },
    {
      eol_product_id: "0ec2d3gd-5104-7h64-c8c1-24262582g24d",
      name: "CentOS",
      product_category: "os",
      description:
        "CentOS is a community-driven free software effort focused on delivering a robust open source ecosystem.",
      is_ecosystem: true,
      matching_name: "CentOS",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_centos_1",
          version: "6",
          release_date: "2011-07-10",
          eol_from: "2020-11-30",
          matching_version: "6",
          created_at: "2025-12-03T10:23:45Z",
          updated_at: "2025-12-03T10:23:45Z",
          services: [
            {
              service_id: "service_id_3",
              service_name: "社内ポータル",
            },
          ],
        },
      ],
    },
  ],
};

export const MOCK_SERVICES_DEADLINE_APPROACHING_ONLY = {
  total: 4,
  products: [
    {
      eol_product_id: "eol_product_id_python",
      name: "Python",
      product_category: "runtime",
      description:
        "Python is a programming language that lets you work quickly and integrate systems more effectively.",
      is_ecosystem: false,
      matching_name: "Python",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_python_3_8",
          version: "3.8",
          release_date: "2019-10-14",
          eol_from: "2026-02-15",
          matching_version: "3.8",
          created_at: "2025-10-01T10:00:00Z",
          updated_at: "2025-10-01T10:00:00Z",
          services: [
            {
              service_id: "service_id_analysis",
              service_name: "データ分析基盤",
            },
          ],
        },
      ],
    },
    {
      eol_product_id: "eol_product_id_alpine",
      name: "Alpine Linux",
      product_category: "os",
      description: "Alpine Linux is a security-oriented, lightweight Linux distribution.",
      is_ecosystem: false,
      matching_name: "Alpine Linux",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_alpine_3_17",
          version: "3.17",
          release_date: "2022-11-22",
          eol_from: "2026-04-01",
          matching_version: "3.17",
          created_at: "2025-10-01T10:00:00Z",
          updated_at: "2025-10-01T10:00:00Z",
          services: [
            {
              service_id: "service_id_edge",
              service_name: "エッジコンピューティングAPI",
            },
          ],
        },
      ],
    },
    {
      eol_product_id: "eol_product_id_redis",
      name: "Redis",
      product_category: "middleware",
      description:
        "Redis is an in-memory data structure store, used as a database, cache, and message broker.",
      is_ecosystem: false,
      matching_name: "Redis",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_redis_6_2",
          version: "6.2",
          release_date: "2021-03-01",
          eol_from: "2026-06-10",
          matching_version: "6.2",
          created_at: "2025-10-01T10:00:00Z",
          updated_at: "2025-10-01T10:00:00Z",
          services: [
            {
              service_id: "service_id_cache",
              service_name: "セッション管理サーバー",
            },
          ],
        },
      ],
    },
    {
      eol_product_id: "eol_product_id_lodash",
      name: "Lodash",
      product_category: "package",
      description:
        "A modern JavaScript utility library delivering modularity, performance & extras.",
      is_ecosystem: true,
      matching_name: "Lodash",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_lodash_4",
          version: "4.17.21",
          release_date: "2021-02-20",
          eol_from: "2026-07-20",
          matching_version: "4.17.21",
          created_at: "2025-10-01T10:00:00Z",
          updated_at: "2025-10-01T10:00:00Z",
          services: [
            {
              service_id: "service_id_frontend",
              service_name: "顧客向けウェブUI",
            },
          ],
        },
      ],
    },
  ],
};

export const MOCK_SERVICES_SUPPORTED_ONLY = {
  total: 4,
  products: [
    {
      eol_product_id: "0ec2d3gd-5344-7h64-c8c1-24262582g24d",
      name: "Node.js",
      product_category: "runtime",
      description: "Node.js is an open-source, cross-platform JavaScript runtime environment.",
      is_ecosystem: false,
      matching_name: "Node.js",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_nodejs_22",
          version: "22.x",
          release_date: "2024-04-23",
          eol_from: "2027-04-30",
          matching_version: "22.x",
          created_at: "2025-01-01T10:00:00Z",
          updated_at: "2025-01-01T10:00:00Z",
          services: [
            {
              service_id: "service_id_1",
              service_name: "最新システム",
            },
          ],
        },
      ],
    },
    {
      eol_product_id: "0a32d3gd-5104-7h64-c8c1-24262582g24d",
      name: "React",
      product_category: "package",
      description: "A JavaScript library for building user interfaces.",
      is_ecosystem: true,
      matching_name: "React",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_react_19",
          version: "19.x",
          release_date: "2024-12-05",
          eol_from: "2028-06-01",
          matching_version: "19.x",
          created_at: "2025-01-01T10:00:00Z",
          updated_at: "2025-01-01T10:00:00Z",
          services: [
            {
              service_id: "service_id_1",
              service_name: "最新システム",
            },
          ],
        },
      ],
    },
    {
      eol_product_id: "0ec2d3gd-5134-7h64-c8c1-24462582g24s",
      name: "Ubuntu",
      product_category: "os",
      description: "Ubuntu is a Linux distribution based on Debian.",
      is_ecosystem: false,
      matching_name: "Ubuntu",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_ubuntu_2404",
          version: "24.04 LTS",
          release_date: "2024-04-25",
          eol_from: "2029-04-01",
          matching_version: "24.04 LTS",
          created_at: "2025-01-01T10:00:00Z",
          updated_at: "2025-01-01T10:00:00Z",
          services: [
            {
              service_id: "service_id_1",
              service_name: "最新システム",
            },
          ],
        },
      ],
    },
    {
      eol_product_id: "5ec2d3gd-5104-7h64-c8c1-24272582g24d",
      name: "PostgreSQL",
      product_category: "middleware",
      description: "PostgreSQL is a powerful, open source object-relational database system.",
      is_ecosystem: false,
      matching_name: "PostgreSQL",
      eol_versions: [
        {
          eol_version_id: "eol_version_id_postgresql_16",
          version: "16",
          release_date: "2023-09-14",
          eol_from: "2028-11-09",
          matching_version: "16",
          created_at: "2025-01-01T10:00:00Z",
          updated_at: "2025-01-01T10:00:00Z",
          services: [
            {
              service_id: "service_id_1",
              service_name: "最新システム",
            },
          ],
        },
      ],
    },
  ],
};

export const MOCK_SERVICES_EMPTY = { total: 0, products: [] };

export const MOCK_SERVICES_DEFAULT = {
  total:
    MOCK_SERVICES_EXPIRED_ONLY.total +
    MOCK_SERVICES_DEADLINE_APPROACHING_ONLY.total +
    MOCK_SERVICES_SUPPORTED_ONLY.total,
  products: [
    ...MOCK_SERVICES_EXPIRED_ONLY.products,
    ...MOCK_SERVICES_DEADLINE_APPROACHING_ONLY.products,
    ...MOCK_SERVICES_SUPPORTED_ONLY.products,
  ],
};
