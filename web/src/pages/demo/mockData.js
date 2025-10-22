const longReasonText =
  'This vulnerability is rated as "High" Impact because it affects a critical, internet-facing authentication service. An exploit could lead to unauthorized access to sensitive customer data, including PII (Personally Identifiable Information). The service is written in Java and uses a vulnerable version of the Log4j library (2.14.1), which is susceptible to CVE-2021-44228 (Log4Shell). Successful exploitation would allow a remote, unauthenticated attacker to execute arbitrary code with the privileges of the application server. This could lead to a full system compromise, data exfiltration, and lateral movement within the production network. Although we have a WAF in place, certain payload encodings may bypass its rules. The service processes user-provided data in log messages, which is the primary attack vector. The combination of high potential damage, ease of exploitation, and the service\'s critical role in our infrastructure justifies the High impact rating. Immediate patching or mitigation is required. This assessment follows the CVSS v3.1 scoring, with the base score calculated as 10.0 (Critical), but we have adjusted the internal safety impact to High to align with our specific business context and risk appetite. The development team has been notified and is actively working on a patch. The expected remediation timeline is 48 hours. During this period, monitoring for anomalous activity related to this service will be intensified. A full post-mortem analysis will be conducted after the incident is resolved to identify any potential gaps in our logging and detection capabilities and to prevent similar vulnerabilities from being introduced in the future. Further details can be found in the internal security advisory document SA-2025-09-17-001.';

export const mockMembers = [
  {
    id: "user1",
    name: "Taro Yamada",
  },
  {
    id: "user2",
    name: "Hanako Suzuki",
  },
  {
    id: "user3",
    name: "Jiro Sato",
  },
  {
    id: "user4",
    name: "Sachiko Tanaka",
  },
];

export const mockVulnerabilities = [
  {
    id: "vuln-001",
    title: "setuptools: Path Traversal Vulnerability",
    tasks: [
      {
        ticket_id: "t1-1",
        target: "webapp/frontend/package.json",
        ticket_handling_status: "In Progress",
        safety_impact: "High",
        safety_impact_change_reason:
          "This component processes user-uploaded files and a path traversal could lead to exposure of sensitive server files.",
        assignees: ["user1"],
      },
      {
        ticket_id: "t1-2",
        target: "backend/api/requirements.txt",
        ticket_handling_status: "Alerted",
        safety_impact: "Medium",
        safety_impact_change_reason: "",
        assignees: [],
      },
      {
        ticket_id: "t1-3",
        target: "batch-processor/pom.xml",
        ticket_handling_status: "Resolved",
        safety_impact: "High",
        safety_impact_change_reason: "Resolved by updating the library to a patched version.",
        assignees: ["user2"],
      },
    ],
  },
  {
    id: "vuln-002",
    title: "pypa/setuptools: Remote code execution",
    tasks: [
      {
        ticket_id: "t2-1",
        target: "data-processor/pom.xml",
        ticket_handling_status: "Open",
        safety_impact: "Catastrophic",
        safety_impact_change_reason: "Default impact assessment based on CVSS score.",
        assignees: [],
      },
    ],
  },
  {
    id: "vuln-003",
    title: "Log4j: Remote Code Execution (Log4Shell)",
    tasks: [
      {
        ticket_id: "t3-1",
        target: "legacy-system/WEB-INF/lib/log4j-core-2.14.1.jar",
        ticket_handling_status: "In Progress",
        safety_impact: "Catastrophic",
        safety_impact_change_reason: longReasonText,
        assignees: ["user3"],
      },
      {
        ticket_id: "t3-2",
        target: "notification-service/build.gradle",
        ticket_handling_status: "In Progress",
        safety_impact: "Catastrophic",
        safety_impact_change_reason: longReasonText,
        assignees: ["user1", "user3"],
      },
    ],
  },
];
