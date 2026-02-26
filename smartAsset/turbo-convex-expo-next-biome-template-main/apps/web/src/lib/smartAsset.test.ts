// biome-ignore lint/style/noRestrictedImports: local workspace uses vitest for unit tests.
import { describe, expect, it } from "vitest";
import {
  ASSETS,
  evaluateInspection,
  recommendedMaintainer,
  roleActions,
} from "./smartAsset";

describe("evaluateInspection", () => {
  it("returns high-priority findings for severe keywords", () => {
    const assessment = evaluateInspection("There is corrosion and leak near a cracked pipe.");
    expect(assessment.overall_priority).toBeGreaterThan(0.75);
    expect(assessment.findings.length).toBeGreaterThanOrEqual(2);
    expect(assessment.actions[0]?.risk_value).toBeGreaterThan(70);
  });

  it("falls back to low-priority baseline when no keywords match", () => {
    const assessment = evaluateInspection("paint is fading and needs cleaning");
    expect(assessment.findings).toHaveLength(1);
    expect(assessment.findings[0]?.type).toBe("general_wear");
    expect(assessment.overall_priority).toBeLessThan(0.5);
  });
});

describe("roleActions", () => {
  it("includes maintenance reporting for maintenance users", () => {
    expect(roleActions("maintenance")).toContain("report_maintenance");
  });

  it("includes approval for supervisors", () => {
    expect(roleActions("supervisor")).toContain("approve_work_order");
  });
});

describe("recommendedMaintainer", () => {
  it("resolves maintainer based on asset mapping", () => {
    const firstAsset = ASSETS[0];
    if (!firstAsset) {
      throw new Error("expected seeded assets");
    }
    const maintainer = recommendedMaintainer(firstAsset);
    expect(maintainer?.name).toBeTruthy();
  });
});
