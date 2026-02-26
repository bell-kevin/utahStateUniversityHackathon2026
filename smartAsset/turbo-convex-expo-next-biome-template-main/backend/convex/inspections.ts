import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { scoreInspection } from "./risk";

function statusFromRisk(riskScore: number) {
  if (riskScore >= 75) {
    return "critical" as const;
  }
  if (riskScore >= 45) {
    return "watch" as const;
  }
  return "healthy" as const;
}

export const recentForAsset = query({
  args: { assetId: v.id("assets") },
  handler: async (ctx: any, args: any) => {
    const inspections = await ctx.db
      .query("inspections")
      .withIndex("by_asset", (q: any) => q.eq("assetId", args.assetId))
      .collect();

    return inspections.sort((a: any, b: any) => b.createdAt - a.createdAt).slice(0, 10);
  },
});

export const submitInspection = mutation({
  args: {
    assetId: v.id("assets"),
    reporterUserId: v.id("users"),
    source: v.union(v.literal("nfc_scan"), v.literal("manual")),
    note: v.string(),
    imageUrl: v.optional(v.string()),
  },
  handler: async (ctx: any, args: any) => {
    const assessment = scoreInspection(args.note);
    const now = Date.now();

    const inspectionId = await ctx.db.insert("inspections", {
      ...args,
      aiSummary: assessment.summary,
      aiPriority: assessment.overallPriority,
      findings: assessment.findings,
      actions: assessment.actions,
      createdAt: now,
    });

    const asset = await ctx.db.get(args.assetId);
    if (asset) {
      const mergedRiskScore = Math.round((asset.riskScore * 0.55 + assessment.overallPriority * 100 * 0.45));
      await ctx.db.patch(asset._id, {
        riskScore: mergedRiskScore,
        lastInspectionAt: now,
        status: statusFromRisk(mergedRiskScore),
      });

      const topAction = assessment.actions[0];
      if (topAction) {
        await ctx.db.insert("workOrders", {
          assetId: asset._id,
          inspectionId,
          title: `${asset.name}: ${topAction.title}`,
          status: "open",
          priority: topAction.priority,
          assigneeUserId: asset.maintainerUserId,
          createdAt: now,
          dueAt: now + 1000 * 60 * 60 * 24,
        });
      }
    }

    return {
      inspectionId,
      assessment,
    };
  },
});
