import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const listByRisk = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx: any, args: any) => {
    const assets = await ctx.db.query("assets").collect();
    return assets
      .sort((a: any, b: any) => b.riskScore - a.riskScore)
      .slice(0, args.limit ?? 25);
  },
});

export const getByTag = query({
  args: { tagId: v.string() },
  handler: async (ctx: any, args: any) => {
    return ctx.db
      .query("assets")
      .withIndex("by_tag", (q: any) => q.eq("tagId", args.tagId))
      .first();
  },
});

export const registerAsset = mutation({
  args: {
    tagId: v.string(),
    name: v.string(),
    category: v.string(),
    location: v.string(),
    ownerTeam: v.string(),
    model: v.optional(v.string()),
    notes: v.optional(v.string()),
  },
  handler: async (ctx: any, args: any) => {
    const existing = await ctx.db
      .query("assets")
      .withIndex("by_tag", (q: any) => q.eq("tagId", args.tagId))
      .first();
    if (existing) {
      return existing._id;
    }

    return ctx.db.insert("assets", {
      ...args,
      status: "healthy",
      riskScore: 0,
      lastInspectionAt: Date.now(),
    });
  },
});

export const recordScan = mutation({
  args: {
    assetId: v.id("assets"),
    userId: v.id("users"),
    action: v.union(
      v.literal("open_menu"),
      v.literal("report_problem"),
      v.literal("inspect_item"),
      v.literal("report_maintenance")
    ),
    latitude: v.optional(v.number()),
    longitude: v.optional(v.number()),
  },
  handler: async (ctx: any, args: any) => {
    return ctx.db.insert("scans", {
      ...args,
      scannedAt: Date.now(),
    });
  },
});
