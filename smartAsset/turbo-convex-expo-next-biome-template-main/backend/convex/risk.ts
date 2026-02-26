export type Finding = {
  type: string;
  severity: number;
  evidence: string;
};

export type SuggestedAction = {
  suggestedKey: string;
  title: string;
  description: string;
  reason: string;
  priority: number;
  riskValue: number;
  recommendedSteps: string[];
  estimatedCost: number;
};

export type AiAssessment = {
  summary: string;
  overallPriority: number;
  findings: Finding[];
  actions: SuggestedAction[];
};

const KEYWORDS: Array<{ needle: string; severity: number; type: string }> = [
  { needle: "corrosion", severity: 0.87, type: "corrosion_detected" },
  { needle: "rust", severity: 0.8, type: "rust_detected" },
  { needle: "leak", severity: 0.9, type: "fluid_leak" },
  { needle: "crack", severity: 0.86, type: "structural_crack" },
  { needle: "frayed", severity: 0.82, type: "cable_fray" },
  { needle: "overheat", severity: 0.88, type: "heat_risk" },
  { needle: "noise", severity: 0.58, type: "abnormal_noise" },
];

export function scoreInspection(note: string): AiAssessment {
  const normalized = note.toLowerCase();
  const findings: Finding[] = KEYWORDS.filter((k) => normalized.includes(k.needle)).map(
    (k) => ({
      type: k.type,
      severity: k.severity,
      evidence: `Keyword '${k.needle}' detected in report note.`,
    })
  );

  if (findings.length === 0) {
    findings.push({
      type: "no_major_issue_detected",
      severity: 0.24,
      evidence: "No high-risk keywords detected. Human validation still recommended.",
    });
  }

  const overallPriority = Math.min(
    1,
    Number(
      (findings.reduce((acc, finding) => acc + finding.severity, 0) / findings.length).toFixed(
        2
      )
    )
  );

  const actions: SuggestedAction[] = findings.map((finding, index) => ({
    suggestedKey: `action_${finding.type}`,
    title:
      finding.severity > 0.8
        ? "Dispatch maintenance immediately"
        : "Schedule next-day inspection",
    description: `Address ${finding.type.replaceAll("_", " ")}.`,
    reason: finding.evidence,
    priority: finding.severity,
    riskValue: Math.round(finding.severity * 100),
    recommendedSteps: [
      "Attach additional close-up photos.",
      "Verify impact radius and public safety concerns.",
      "Assign responsible maintainer.",
    ],
    estimatedCost: Number((120 + index * 45 + finding.severity * 180).toFixed(2)),
  }));

  return {
    summary:
      overallPriority > 0.75
        ? "High risk condition detected. Immediate attention recommended."
        : "Issue detected and prioritized for maintenance workflow.",
    overallPriority,
    findings,
    actions,
  };
}
