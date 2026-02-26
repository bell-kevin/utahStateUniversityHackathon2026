export type Role = "student" | "maintenance" | "supervisor";

export type User = {
  id: string;
  name: string;
  role: Role;
  zone: string;
};

export type Asset = {
  id: string;
  tagId: string;
  name: string;
  location: string;
  category: string;
  riskScore: number;
  status: "healthy" | "watch" | "critical";
  maintainerId: string;
};

export type AiFinding = {
  type: string;
  severity: number;
  evidence: string;
};

export type AiAction = {
  suggested_key: string;
  title: string;
  description: string;
  reason: string;
  priority: number;
  risk_value: number;
  recommended_steps: string[];
  estimated_cost: number;
};

export type AiResponse = {
  summary: string;
  overall_priority: number;
  findings: AiFinding[];
  actions: AiAction[];
};

export const USERS: User[] = [
  { id: "u1", name: "Avery Student", role: "student", zone: "Engineering" },
  { id: "u2", name: "Jordan Tech", role: "maintenance", zone: "Engineering" },
  { id: "u3", name: "Riley Ops", role: "supervisor", zone: "Campus Core" },
];

export const ASSETS: Asset[] = [
  {
    id: "a1",
    tagId: "NFC-USU-1001",
    name: "HVAC Compressor A",
    location: "Engineering Building Roof",
    category: "HVAC",
    riskScore: 64,
    status: "watch",
    maintainerId: "u2",
  },
  {
    id: "a2",
    tagId: "NFC-USU-2088",
    name: "West Hall Water Pump",
    location: "West Hall Basement",
    category: "Plumbing",
    riskScore: 31,
    status: "healthy",
    maintainerId: "u2",
  },
  {
    id: "a3",
    tagId: "NFC-USU-0192",
    name: "Library Elevator Panel",
    location: "Merrill-Cazier Library",
    category: "Electrical",
    riskScore: 81,
    status: "critical",
    maintainerId: "u3",
  },
];

const RISK_KEYWORDS: Array<{ word: string; severity: number; findingType: string }> = [
  { word: "corrosion", severity: 0.9, findingType: "corrosion" },
  { word: "rust", severity: 0.78, findingType: "rust" },
  { word: "leak", severity: 0.88, findingType: "leak" },
  { word: "smoke", severity: 0.95, findingType: "smoke_risk" },
  { word: "sparks", severity: 0.92, findingType: "electrical_sparks" },
  { word: "crack", severity: 0.84, findingType: "structural_crack" },
  { word: "loose", severity: 0.54, findingType: "loose_component" },
];

export function evaluateInspection(note: string): AiResponse {
  const lower = note.toLowerCase();
  const findings = RISK_KEYWORDS.filter(({ word }) => lower.includes(word)).map((item) => ({
    type: item.findingType,
    severity: item.severity,
    evidence: `Detected '${item.word}' in user report text.`,
  }));

  const normalizedFindings =
    findings.length > 0
      ? findings
      : [
          {
            type: "general_wear",
            severity: 0.35,
            evidence: "No high-severity keywords detected; flagging for routine inspection.",
          },
        ];

  const overall = Number(
    (
      normalizedFindings.reduce((total, finding) => total + finding.severity, 0) /
      normalizedFindings.length
    ).toFixed(2)
  );

  const actions = normalizedFindings.map((finding) => ({
    suggested_key: `address_${finding.type}`,
    title: finding.severity > 0.8 ? "Immediate maintenance dispatch" : "Schedule inspection",
    description: `Resolve ${finding.type.replaceAll("_", " ")} on selected asset.`,
    reason: finding.evidence,
    priority: finding.severity,
    risk_value: Math.round(finding.severity * 100),
    recommended_steps: [
      "Capture close-up evidence photo.",
      "Verify hazard for nearby occupants.",
      "Assign maintainer and due date.",
    ],
    estimated_cost: Number((150 + finding.severity * 400).toFixed(2)),
  }));

  return {
    summary:
      overall > 0.75
        ? "Critical risk trend detected. Prioritize this asset immediately."
        : "Inspection captured. Recommended actions were generated.",
    overall_priority: overall,
    findings: normalizedFindings,
    actions,
  };
}

export function roleActions(role: Role): string[] {
  if (role === "maintenance") {
    return ["report_problem", "inspect_item", "report_maintenance", "view_history"];
  }
  if (role === "supervisor") {
    return ["report_problem", "inspect_item", "approve_work_order", "view_history"];
  }
  return ["report_problem", "inspect_item", "view_history"];
}

export function recommendedMaintainer(asset: Asset): User | undefined {
  return USERS.find((user) => user.id === asset.maintainerId);
}
